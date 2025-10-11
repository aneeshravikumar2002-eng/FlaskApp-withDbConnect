pipeline {
    agent any

    environment {
        DOCKERHUB_CRED = credentials('dockerhub-login') // Docker Hub credentials
        SONAR_TOKEN    = credentials('sonar-token')    // SonarQube token
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out repository...'
                git branch: 'main', url: 'https://github.com/aneeshravikumar2002-eng/FlaskApp-withDbConnect.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def mvn
                    try {
                        mvn = tool 'Default Maven'
                        echo "Maven found at: ${mvn}"
                    } catch (err) {
                        error """
                        Maven tool 'Default Maven' not found!
                        Please configure Maven in Jenkins under:
                        Manage Jenkins → Global Tool Configuration → Maven
                        """
                    }

                    // Run SonarQube securely
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_SECURE')]) {
                        withSonarQubeEnv('My SonarQube Server') {
                            sh """#!/bin/bash
                            ${mvn}/bin/mvn clean verify sonar:sonar \
                                -Dsonar.projectKey=flask-sonar \
                                -Dsonar.projectName='flask-sonar' \
                                -Dsonar.login=$SONAR_TOKEN_SECURE
                            """
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh """
                    docker build -t aneesh292002/flask-app:${BUILD_NUMBER} \
                                 -t aneesh292002/flask-app:latest .
                """
            }
        }

        stage('Run Docker Container') {
            steps {
                echo 'Running Docker container...'
                sh """
                    docker stop flask-container || true
                    docker rm flask-container || true
                    docker run -d --name flask-container -p 5001:5000 aneesh292002/flask-app:latest
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-login', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """#!/bin/bash
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push aneesh292002/flask-app:${BUILD_NUMBER}
                        docker push aneesh292002/flask-app:latest
                        docker logout
                    """
                }
            }
        }
    }

    post {
        failure {
            echo 'Build failed. Docker artifacts may still be available for debugging.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}
