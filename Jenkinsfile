pipeline {
    agent any

    environment {
        DOCKERHUB_USER = credentials('dockerhub-login') // Docker Hub credentials
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
                    // Try to get Maven tool
                    def mvn
                    try {
                        mvn = tool 'Default Maven'
                        echo "Maven found at: ${mvn}"
                    } catch (err) {
                        error """
                        Maven tool 'Default Maven' not found!
                        Please configure Maven in Jenkins under:
                        Manage Jenkins → Global Tool Configuration → Maven
                        and make sure the name matches exactly.
                        """
                    }

                    // Run SonarQube analysis
                    withSonarQubeEnv('My SonarQube Server') {
                        sh """
                            ${mvn}/bin/mvn clean verify sonar:sonar \
                                -Dsonar.projectKey=flask-sonar \
                                -Dsonar.projectName='flask-sonar' \
                                -Dsonar.login=${SONAR_TOKEN}
                        """
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
                withCredentials([usernamePassword(credentialsId: 'dockerhub-login', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh """
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
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

