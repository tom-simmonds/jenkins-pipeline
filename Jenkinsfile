node {
    stage('Checkout') {
        checkout scm
    }

    stage('Build') {
        sh 'python3 app.py'
    }

    stage('Test') {
        sh 'python3 test_app.py'
    }

    stage('Deploy') {
        sh 'echo "Deploying application..."'
    }
}