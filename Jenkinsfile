pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        IMAGE_NAME = 'ahmadazizwirawidodo/simple-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Docker') {
            steps {
                bat 'docker version'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-test',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    powershell '''
                        $ErrorActionPreference = 'Stop'

                        if ([string]::IsNullOrWhiteSpace($env:DOCKERHUB_USER)) {
                            throw 'Username credential Jenkins kosong'
                        }

                        if ([string]::IsNullOrWhiteSpace($env:DOCKERHUB_TOKEN)) {
                            throw 'Token credential Jenkins kosong'
                        }

                        $username = $env:DOCKERHUB_USER.Trim()
                        $token = $env:DOCKERHUB_TOKEN.Trim()

                        if ($username -ne 'auraiftitahh') {
                            throw 'Username credential tidak sesuai'
                        }

                        $configDir = Join-Path $env:TEMP (
                            'jenkins-docker-' + [guid]::NewGuid().ToString()
                        )

                        New-Item -ItemType Directory -Path $configDir |
                            Out-Null

                        $configFile = Join-Path $configDir 'config.json'

                        try {
                            $auth = [Convert]::ToBase64String(
                                [Text.Encoding]::UTF8.GetBytes(
                                    "${username}:${token}"
                                )
                            )

                            $config = @{
                                auths = @{
                                    'https://index.docker.io/v1/' = @{
                                        auth = $auth
                                    }
                                }
                            } | ConvertTo-Json -Depth 5

                            [IO.File]::WriteAllText(
                                $configFile,
                                $config,
                                [Text.UTF8Encoding]::new($false)
                            )

                            Write-Output 'Push menggunakan credential konfigurasi sementara'

                            docker --config "$configDir" push "${env:IMAGE_NAME}:${env:BUILD_NUMBER}"
                            if ($LASTEXITCODE -ne 0) {
                                throw 'Push image bernomor gagal'
                            }

                            docker tag "${env:IMAGE_NAME}:${env:BUILD_NUMBER}" "${env:IMAGE_NAME}:latest"
                            if ($LASTEXITCODE -ne 0) {
                                throw 'Pembuatan tag latest gagal'
                            }

                            docker --config "$configDir" push "${env:IMAGE_NAME}:latest"
                            if ($LASTEXITCODE -ne 0) {
                                throw 'Push latest gagal'
                            }

                            Write-Output 'Image bernomor dan latest berhasil di-push'
                        }
                        finally {
                            if (Test-Path -LiteralPath $configFile) {
                                Remove-Item -LiteralPath $configFile -Force
                            }

                            $auth = $null
                            $config = $null
                            $token = $null
                        }
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Build dan push image Docker berhasil.'
        }

        failure {
            echo 'Pipeline gagal. Periksa Console Output.'
        }
    }
}
