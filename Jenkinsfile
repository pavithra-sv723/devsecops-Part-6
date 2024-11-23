pipeline {
    agent any
    tools {
        maven 'Maven_3_2_5'
    }
    environment {
        SONARQUBE_URL = 'https://sonarcloud.io/project/overview?id=pavithra-devops_devsecops'
        SONARQUBE_TOKEN = '768ee2edc76f25fa11240f65b225527718b02f30'
        JIRA_URL = 'https://devsync.atlassian.net/jira/software/projects/DEV/boards/2'
        JIRA_USER = 'Pavithra'
        JIRA_API_TOKEN = 'ATCTT3xFfGN0H-n0va10BPiOWLQ-tdnhhOZ6UZYNM68hcACB4XLvmuy6qwP1aRHHMZTf2R3m9rwPbcndp3f7AyJfn_3RwNICoKU-cgFqQqGoZnXx5e69Sl_RgVHOa38138mSoeMNc94W4-kRx25PDVX86SgsWgQICiEQeX6HcH_joC67Nb6OlZs=50F87329'
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

        pipeline {
    agent any
    
    environment {
        SONARQUBE_URL = 'http://your-sonarqube-server'
        SONARQUBE_TOKEN = 'your-sonarqube-token'
        JIRA_URL = 'http://your-jira-server'
        JIRA_USER = 'your-jira-username'
        JIRA_API_TOKEN = 'your-jira-api-token'
    }
    
    stages {
        stage('SonarQube Analysis') {
            steps {
                script {
                    // Trigger SonarQube analysis
                    withSonarQubeEnv('SonarQube') {
                        sh 'mvn clean verify sonar:sonar -Dsonar.projectKey=your-project-key'
                    }
                }
            }
        }
        
        stage('Check SonarQube Issues') {
            steps {
                script {
                    // Fetch issues from SonarQube
                    def sonarIssues = sh(script: "curl -s -u ${SONARQUBE_TOKEN}: ${SONARQUBE_URL}/api/issues/search?severity=CRITICAL&componentKeys=your-project-key", returnStdout: true).trim()

                    // Check if any critical issues exist
                    if (sonarIssues.contains('\"total\":0')) {
                        echo 'No critical issues found.'
                    } else {
                        echo 'Critical issues detected.'
                        sendJiraNotification(sonarIssues)
                    }
                }
            }
        }
    }
}

    def sendJiraNotification(issues) {
        // Construct the Jira issue creation payload based on the detected issues
        def issueSummary = "Critical issues found in SonarQube"
        def issueDescription = "The following critical issues were detected: ${issues}"
    
        def response = sh(script: """
            curl -u ${JIRA_USER}:${JIRA_API_TOKEN} -X POST \
            --data '{"fields": {"project": {"key": "YOUR_PROJECT_KEY"}, "summary": "${issueSummary}", "description": "${issueDescription}", "issuetype": {"name": "Bug"}}}' \
            -H "Content-Type: application/json" ${JIRA_URL}/rest/api/2/issue/
        """, returnStdout: true).trim()
    
        echo "Jira issue created: ${response}"
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
    }
}
