pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = 'romacheredov'
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/lab3_ml_model"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('app') {
                    // Собираем образ. Requirements установятся внутри Dockerfile автоматически.
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Test in Docker') {
            steps {
                // Запускаем только что собранный образ и прогоняем тесты внутри него
                sh "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest tests/test_api.py"
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USER')]) {
                    sh "echo \$DOCKERHUB_PASSWORD | docker login -u \$DOCKERHUB_USER --password-stdin"
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }
    }

    post {
        always {
            sh "docker logout"
        }
    }
}