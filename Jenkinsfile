pipeline {
    // Runs on the Jenkins container built from my-jenkins/Dockerfile, which has
    // Python 3 and the OS libraries Playwright needs.
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['ci', 'dev'],
            description: 'Config file to load from config/environments/<name>.yaml'
        )
        choice(
            name: 'MARKER',
            choices: ['all', 'smoke', 'e2e'],
            description: 'Which pytest-bdd tag to run (pytest.ini: smoke, e2e)'
        )
        string(
            name: 'FEATURE_FILE',
            defaultValue: '',
            description: 'Optional: only run this feature file, e.g. login.feature'
        )
        booleanParam(
            name: 'PARALLEL',
            defaultValue: false,
            description: 'Run scenarios in parallel across CPUs (pytest-xdist -n auto)'
        )
    }

    environment {
        TEST_ENV = "${params.TEST_ENV}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .ci-venv
                    . .ci-venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    playwright install chromium
                '''
            }
        }

        stage('Run tests') {
            steps {
                script {
                    def markerArg = params.MARKER == 'all' ? '' : "-m ${params.MARKER}"
                    def featureArg = params.FEATURE_FILE?.trim()
                        ? "--feature-file=${params.FEATURE_FILE}"
                        : ''
                    def parallelArg = params.PARALLEL ? '-n auto' : ''

                    // '|| true' so a failed test run still reaches the post block
                    // (report publishing, archiving) instead of aborting the stage outright.
                    sh """
                        . .ci-venv/bin/activate
                        pytest ${markerArg} ${featureArg} ${parallelArg} \
                            --junitxml=reports/junit.xml \
                            || true
                    """
                }
            }
        }

        stage('Evaluate results') {
            steps {
                script {
                    if (!fileExists('reports/junit.xml')) {
                        error('reports/junit.xml was not produced - test run did not complete')
                    }
                    def junit = readFile('reports/junit.xml')
                    if (junit.contains('<failure') || junit.contains('<error')) {
                        error('One or more scenarios failed - see the JUnit / HTML report for details')
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit.xml'

            publishHTML(target: [
                reportName: 'Automation Test Report',
                reportDir: 'reports',
                reportFiles: 'custom_test_report.html',
                keepAll: true,
                alwaysLinkToLastBuild: true,
                allowMissing: true
            ])

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true, fingerprint: true
        }
        failure {
            echo "Build failed - check the JUnit results and HTML report (${env.BUILD_URL}) for details."
        }
    }
}
