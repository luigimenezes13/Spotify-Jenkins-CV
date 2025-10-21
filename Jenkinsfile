pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.12'
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
                echo 'Configurando ambiente Python...'
                sh '''
                    # Instalar Python via pyenv
                    curl https://pyenv.run | bash
                    export PYENV_ROOT="$HOME/.pyenv"
                    export PATH="$PYENV_ROOT/bin:$PATH"
                    eval "$(pyenv init -)"
                    pyenv install ${PYTHON_VERSION}
                    pyenv global ${PYTHON_VERSION}
                    
                    # Verificar versão
                    python --version
                    pip --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Instalando dependências...'
                sh '''
                    # Criar ambiente virtual
                    python -m venv venv
                    source venv/bin/activate
                    
                    # Instalar dependências
                    pip install --upgrade pip setuptools wheel
                    pip install -e .[dev]
                '''
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Executando linting...'
                sh '''
                    source venv/bin/activate
                    ruff check app/ tests/
                '''
            }
        }
        
        stage('Format Check') {
            steps {
                echo 'Verificando formatação...'
                sh '''
                    source venv/bin/activate
                    black --check app/ tests/
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Executando testes...'
                sh '''
                    source venv/bin/activate
                    pytest --cov=app --cov-report=html --cov-report=term
                '''
            }
            post {
                always {
                    echo 'Publicando relatório de cobertura...'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
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
