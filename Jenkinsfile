@Library('jenkins-shared-library') _

node {
    stage('Checkout') {
        checkout scm
    }

    buildPython()
}