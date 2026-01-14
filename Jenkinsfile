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
                    # In ra để kiểm tra file trước khi sửa
                    cat deployment.yaml
                    
                    # QUAN TRỌNG: Dùng nháy kép " để biến ${IMAGE_TAG} và ${APP_NAME} hoạt động
                    # Dùng dấu : để phân tách rõ ràng tên image và tag
                    sed -i "s/${APP_NAME}:.*/${APP_NAME}:${IMAGE_TAG}/g" deployment.yaml
                    
                    # In ra để xác nhận lệnh sed đã thay đổi đúng số build chưa
                    cat deployment.yaml
                """
            }
        }

        stage("Push the changed deployment file to Git") {
            steps {
                script {
                    sh """
                        git config --global user.name "sangnt8386"
                        git config --global user.email "nguyenthesang14@gmail.com"
                        git add deployment.yaml
                        
                        # Chỉ commit nếu có sự thay đổi (tránh lỗi 'nothing to commit')
                        if [ -n "\$(git status --porcelain)" ]; then
                            git commit -m "Update image tag to ${IMAGE_TAG} [skip ci]"
                            echo "Changes committed"
                        else
                            echo "No changes to commit"
                        fi
                    """
                    
                    
                    withCredentials([gitUsernamePassword(credentialsId: 'github', gitToolName: 'Default')]) {
                        sh "git push https://github.com/sangnt8386/gitops-feedback-app.git main"
                    }
                }
            }
        }
      
    }
}
