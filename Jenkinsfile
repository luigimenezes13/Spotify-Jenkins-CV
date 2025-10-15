pipeline {
    agent any
    
    environment {
        NODE_VERSION = '18.18.0'
        PNPM_VERSION = '8.15.0'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Fazendo checkout do código...'
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Configurando ambiente Node.js e pnpm...'
                sh '''
                    # Instalar Node.js via nvm
                    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                    export NVM_DIR="$HOME/.nvm"
                    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
                    nvm install ${NODE_VERSION}
                    nvm use ${NODE_VERSION}
                    
                    # Instalar pnpm
                    npm install -g pnpm@${PNPM_VERSION}
                    
                    # Verificar versões
                    node --version
                    pnpm --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Instalando dependências...'
                sh 'pnpm install --frozen-lockfile'
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Executando linting...'
                sh 'pnpm run lint'
            }
        }
        
        stage('Format Check') {
            steps {
                echo 'Verificando formatação...'
                sh 'pnpm run format:check'
            }
        }
        
        stage('Type Check') {
            steps {
                echo 'Verificando tipos TypeScript...'
                sh 'pnpm run build'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Executando testes...'
                sh 'pnpm run test:coverage'
            }
            post {
                always {
                    echo 'Publicando relatório de cobertura...'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'coverage/lcov-report',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Construindo imagem Docker...'
                script {
                    def image = docker.build("spotify-jenkins-cv:${env.BUILD_NUMBER}")
                    docker.withRegistry('', 'docker-registry-credentials') {
                        image.push("latest")
                        image.push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Fazendo deploy para staging...'
                // Adicionar comandos de deploy para staging aqui
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Fazendo deploy para produção...'
                // Adicionar comandos de deploy para produção aqui
            }
        }
    }
    
    post {
        always {
            echo 'Limpando workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline executado com sucesso! ✅'
        }
        failure {
            echo 'Pipeline falhou! ❌'
            // Adicionar notificações de falha aqui (email, Slack, etc.)
        }
        unstable {
            echo 'Pipeline instável! ⚠️'
        }
    }
}
