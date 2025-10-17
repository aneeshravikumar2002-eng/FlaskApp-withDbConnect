pipeline {
    agent any

    environment {
        DOCKERHUB_USER = credentials('dockerhub-login') 
    }

    stages {
        stage('git clone') {
            steps {
                echo 'Checking out repository...'
                git branch: 'main', url: 'https://github.com/aneeshravikumar2002-eng/FlaskApp-withDbConnect.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t aneesh292002/beautiful-flask-app:${BUILD_NUMBER} \
                                 -t aneesh292002/beautiful-flask-app:latest .
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                echo 'Running Docker container...'
                sh '''
                    docker stop beautiful-flask-container || true
                    docker rm beautiful-flask-container || true
                    docker run -d --name beautiful-flask-container -p 5000:5000 aneesh292002/beautiful-flask-app:latest
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-login', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh '''
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        docker push aneesh292002/beautiful-flask-app:${BUILD_NUMBER}
                        docker push aneesh292002/beautiful-flask-app:latest
                        docker logout
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script{  
                    def scannerHome = tool 'SonarScanner' 
                    withSonarQubeEnv('My SonarQube Server') { 
                        sh "${scannerHome}/bin/sonar-scanner         
                }
            }
        }
    }

    post {
        failure {
            echo 'Build failed. Keeping Docker artifacts for debugging.'
        }
        successful {
            echo 'Build success'     
            
    }
}
