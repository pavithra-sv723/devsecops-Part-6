pipeline {
    agent any
    tools {
        maven 'Maven_3_2_5'
    }
    environment {
        ZAP_REPORT = "/var/lib/jenkins/workspace/pavithra_devsecops-2/zap_report.html" // Path to the ZAP report
        JIRA_CREDENTIALS_ID = "jira"    // Jenkins credentials ID for JIRA
        JIRA_PROJECT_KEY = "DEV-1"      // JIRA project key
    }
    stages {
        stage('Compile and Run Sonar Analysis') {
            steps {
                sh '''
                    mvn clean verify sonar:sonar \
                    -Dsonar.projectKey=pavithra-devops_devsecops \
                    -Dsonar.organization=pavithra-devops \
                    -Dsonar.host.url=https://sonarcloud.io \
                    -Dsonar.token=768ee2edc76f25fa11240f65b225527718b02f30
                '''
            }
        }

        stage('Run SCA Analysis Using Snyk') {
            steps {
                withCredentials([string(credentialsId: 'SNYK_TOKEN', variable: 'SNYK_TOKEN')]) {
                    sh 'mvn snyk:test -fn'
                }
            }
        }

        stage('Build') {
            steps {
                withDockerRegistry([credentialsId: "dockerlogin", url: ""]) {
                    script {
                        app = docker.build("pavi_img")
                    }
                }
            }
        }

        stage('Push') {
            steps {
                script {
                    docker.withRegistry('https://535002889690.dkr.ecr.us-east-2.amazonaws.com', 'ecr:us-east-2:aws-credentials') {
                        app.push("latest")
                    }
                }
            }
        }

        stage('Kubernetes Deployment of EasyBuggy Web Application') {
            steps {
                withKubeConfig([credentialsId: 'kubelogin']) {
                    sh 'kubectl delete all --all -n devsecops'
                    sh 'kubectl apply -f deployment.yaml --namespace=devsecops'
                }
            }
        }

        stage('Wait for Testing') {
            steps {
                sh '''
                    pwd
                    sleep 90
                    echo "Application has been deployed on K8S"
                '''
            }
        }

        stage('Run DAST Using ZAP') {
            steps {
                withKubeConfig([credentialsId: 'kubelogin']) {
                    sh '''
                        zap.sh -cmd -quickurl http://$(kubectl get services/easybuggy --namespace=devsecops -o json | jq -r ".status.loadBalancer.ingress[] | .hostname") \
                        -quickprogress -quickout ${WORKSPACE}/zap_report.html
                    '''
                    archiveArtifacts artifacts: 'zap_report.html'
                }
            }
        }

        stage('Parse ZAP Report') {
            steps {
                echo "Parsing ZAP report for medium vulnerabilities..."
                script {
                    def vulnerabilities = sh(
                        script: "python3 scripts/parse_zap_report.py ${ZAP_REPORT}",
                        returnStdout: true
                    ).trim()

                    if (vulnerabilities) {
                        echo "Medium vulnerabilities found:"
                        echo vulnerabilities
                        currentBuild.description = "Medium vulnerabilities found in ZAP scan"
                        currentBuild.result = 'UNSTABLE'

                        // Save the vulnerabilities for the next stage
                        env.MEDIUM_VULNERABILITIES = vulnerabilities
                    } else {
                        echo "No Medium vulnerabilities found."
                        currentBuild.description = "No Medium vulnerabilities found"
                    }
                }
            }
        }

        stage('Create JIRA Ticket') {
            when {
                expression {
                    return env.MEDIUM_VULNERABILITIES != null
                }
            }
            steps {
                echo "Creating JIRA ticket for medium vulnerabilities..."
                withCredentials([usernamePassword(
                    credentialsId: env.JIRA_CREDENTIALS_ID, 
                    usernameVariable: 'JIRA_USER', 
                    passwordVariable: 'JIRA_PASS'
                )]) {
                    sh """
                        curl -u $JIRA_USER:$JIRA_PASS \
                            -X POST \
                            -H "Content-Type: application/json" \
                            --data '{
                                "fields": {
                                    "project": { "key": "${JIRA_PROJECT_KEY}" },
                                    "summary": "Medium Vulnerabilities Found in OWASP ZAP Scan",
                                    "description": "${env.MEDIUM_VULNERABILITIES}",
                                    "issuetype": { "name": "Bug" }
                                }
                            }' https://your-jira-instance/rest/api/2/issue/
                    """
                }
            }
        }
    }
}
