pipeline {
    agent any
    tools { 
        maven 'Maven_3_2_5'  
    }
    stages {
        stage('CompileandRunSonarAnalysis') {
            steps {	
                sh 'mvn clean verify sonar:sonar -Dsonar.projectKey=pavithra-devops_devsecops_sample-code -Dsonar.organization=pavithra-devops -Dsonar.host.url=https://sonarcloud.io -Dsonar.token=768ee2edc76f25fa11240f65b225527718b02f30'
            }
        }

        stage('RunSCAAnalysisUsingSnyk') {
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
                    docker.withRegistry('https://535002889690.dkr.ecr.us-east-2.amazonaws.com', 'ecr:us-east-1:aws-credentials') {
                        app.push("latest")
                    }
                }
            }
        }
	   
        stage('wait_for_testing') {
            steps {
                sh 'pwd; sleep 180; echo "Application has been deployed on K8S"'
            }
        }
	   
        stage('RunDASTUsingZAP') {
            steps {
                withKubeConfig([credentialsId: 'kubelogin']) {
                    script {
                        // Run ZAP and generate the report
                        sh 'zap.sh -cmd -quickurl http://$(kubectl get services/easybuggy --namespace=devsecops -o json | jq -r ".status.loadBalancer.ingress[] | .hostname") -quickprogress -quickout ${WORKSPACE}/zap_report.html'

                        // Archive the report
                        archiveArtifacts artifacts: 'zap_report.html'

                        // Parse ZAP Report and create JIRA issues
                        def zapReport = readFile("${WORKSPACE}/zap_report.html") // Read the ZAP report
                        def vulnerabilities = parseZapReport(zapReport) // Parse vulnerabilities (method defined below)

                        // Create JIRA issues for each vulnerability
                        def jiraServer = 'jira' // JIRA server configuration in Jenkins
                        for (vuln in vulnerabilities) {
                            def testIssue = [
                                fields: [
                                    project: [id: '10000'], 
                                    summary: "Vulnerability Found: ${vuln.name}",
                                    description: """
                                        Severity: ${vuln.severity}
                                        URL: ${vuln.url}
                                        Description: ${vuln.description}
                                    """,
                                    issuetype: [name: 'Bug'], 
                                    assignee: [username: 'Pavithra']
                                ]
                            ]
                            def response = jiraNewIssue(issue: testIssue, site: jiraServer)
                            echo "Created JIRA Ticket: ${response.data.key}"
                        }
                    }
                }
            }
        }
    }
}

// Helper function to parse ZAP report and extract vulnerabilities
def parseZapReport(reportContent) {
    // Placeholder function: Parse ZAP report and return a list of vulnerabilities
    // Each vulnerability contains 'name', 'severity', 'url', and 'description'.
    // Actual implementation depends on the ZAP report format (e.g., XML or HTML parsing).
    def vulnerabilities = []
    // Example vulnerability for demonstration
    vulnerabilities << [
        name: "SQL Injection",
        severity: "High",
        url: "http://example.com/vulnerable-endpoint",
        description: "The application is vulnerable to SQL injection."
    ]
    return vulnerabilities
}
