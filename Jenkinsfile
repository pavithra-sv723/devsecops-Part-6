pipeline {
    agent any
    tools {
        maven 'Maven_3_2_5'
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
                    sleep 180
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

                script {
                    // Parse the report to check for vulnerabilities
                    def zapReport = readFile("${WORKSPACE}/zap_report.html")
                    
                    if (zapReport.contains('Medium')) { // Example logic; adjust to actual report format
                        jiraComment(
                            issueKey: 'DEV',  // Replace with your Jira issue key
                            comment: 'Vulnerability detected by OWASP ZAP scan: Medium risk vulnerability found.'
                        )
                    }
                }
            }
        }
    }
}
