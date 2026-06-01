node {
    stage('Checkout') {
        checkout scm
    }

    stage('Build') {
        sh 'python3 -c "from app import calculate; print(calculate(10, 5, \'+\'))"'
    }

    stage('Test') {
        sh 'python3 test_app.py'
    }

    stage('Deploy') {
        sh 'echo "Deploying application..."'
    }
}