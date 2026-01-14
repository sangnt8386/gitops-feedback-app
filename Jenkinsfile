pipeline {
    agent { label "Jenkins-Agent" }
    environment {
              APP_NAME = "flask-app-pipeline"
    }

    stages {
        stage("Cleanup Workspace") {
            steps {
                cleanWs()
            }
        }

        stage("Checkout Code") {
            steps {
                git branch: 'main',
                    credentialsId: 'github',
                    url: 'https://github.com/sangnt8386/gitops-feedback-app'
            }
        }

        stage("Update the Deployment Tags") {
            steps {
                sh """
                   cat deployment.yaml
                   sed -i 's/${APP_NAME}.*/${APP_NAME}:${IMAGE_TAG}/g' deployment.yaml
                   cat deployment.yaml
                """
            }
        }

        stage("Push the changed deployment file to Git") {
            steps {
                sh """
                   git config --global user.name "sangnt8386"
                   git config --global user.email "nguyenthesang14@gmail.com"
                   git add deployment.yaml
                   git commit -m "Updated Deployment Manifest"
                """
                withCredentials([gitUsernamePassword(credentialsId: 'github', gitToolName: 'Default')]) {
                  sh "git push https://github.com/sangnt8386/gitops-feedback-app main"
                }
            }
        }
      
    }
}
