# 🚀 Guia de Configuração do Jenkins

## 📋 Comandos para Rodar o Jenkins

### 1. Instalar e Iniciar Jenkins
```bash
# Instalar Jenkins via Docker
docker run -d --name jenkins-server \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# Verificar se está rodando
docker ps | grep jenkins

# Aguardar inicialização (30-60 segundos)
sleep 30
```

### 2. Obter Senha Inicial
```bash
# Obter senha inicial do Jenkins
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Verificar Status
```bash
# Testar se Jenkins está acessível
curl -I http://localhost:8080

# Ver logs do Jenkins
docker logs jenkins-server
```

## 🔑 Credenciais de Acesso
- **URL**: http://localhost:8080
- **Usuário**: admin
- **Senha inicial**: Execute o comando acima para obter

## 📋 Configuração Inicial no Navegador

### 1. Acesso Inicial
1. Abra o navegador e acesse: http://localhost:8080
2. Cole a senha inicial obtida no comando anterior
3. Clique em "Continue"

### 2. Instalar Plugins
1. Selecione "Install suggested plugins"
2. Aguarde a instalação (pode demorar alguns minutos)
3. Clique em "Continue"

### 3. Criar Usuário Admin
1. Preencha os dados do usuário admin
2. Clique em "Save and Continue"
3. Mantenha a URL: http://localhost:8080/
4. Clique em "Save and Finish"

### 4. Configurar Pipeline

#### 4.1 Criar Novo Job
1. Clique em "New Item"
2. Digite o nome: `spotify-jenkins-cv`
3. Selecione "Pipeline"
4. Clique em "OK"

#### 4.2 Configurar Pipeline
1. Na seção "Pipeline":
   - **Definition**: "Pipeline script from SCM"
   - **SCM**: Git
   - **Repository URL**: `/home/luigimenezes/estudos/cv/PUCC/Spotify-Jenkins-CV`
   - **Script Path**: `Jenkinsfile`
2. Clique em "Save"

### 5. Executar Pipeline
1. Clique em "Build Now"
2. Acompanhe o progresso clicando no build
3. Verifique os logs em tempo real

## 🧪 Comandos de Teste

### Verificar Status do Jenkins
```bash
# Verificar se está rodando
docker ps | grep jenkins

# Verificar logs
docker logs jenkins-server

# Testar acesso
curl -I http://localhost:8080
```

### Executar Testes Localmente
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar testes
python -m pytest tests/ -v

# Executar com cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

### Comandos de Gerenciamento
```bash
# Parar Jenkins
docker stop jenkins-server

# Iniciar Jenkins
docker start jenkins-server

# Reiniciar Jenkins
docker restart jenkins-server

# Remover Jenkins (cuidado!)
docker stop jenkins-server && docker rm jenkins-server
```

## 🔧 Troubleshooting

### Jenkins não inicia
```bash
# Reiniciar container
docker restart jenkins-server

# Verificar logs
docker logs jenkins-server -f
```

### Pipeline falha
1. Verificar se Python 3.12 está disponível
2. Verificar se dependências estão instaladas
3. Verificar permissões de arquivo
4. Verificar logs do build

### Problemas de Porta
```bash
# Verificar portas em uso
ss -tlnp | grep :8080
ss -tlnp | grep :50000

# Parar outros serviços se necessário
sudo lsof -ti:8080 | xargs kill -9
```

## 📊 Monitoramento

### Logs do Jenkins
```bash
# Logs em tempo real
docker logs jenkins-server -f

# Logs específicos
docker exec jenkins-server tail -f /var/jenkins_home/logs/jenkins.log
```

### Status dos Builds
- Acesse: http://localhost:8080/job/spotify-jenkins-cv/
- Verifique histórico de builds
- Analise relatórios de cobertura

## 🎯 Próximos Passos

1. **Configurar Webhooks** para build automático
2. **Integrar com GitHub** (se aplicável)
3. **Configurar Deploy** para staging/produção
4. **Adicionar Notificações** (email, Slack)
5. **Configurar Backup** dos dados do Jenkins

## 📚 Recursos Úteis

- **Documentação Jenkins**: https://www.jenkins.io/doc/
- **Pipeline Syntax**: https://www.jenkins.io/doc/book/pipeline/syntax/
- **Docker Jenkins**: https://hub.docker.com/r/jenkins/jenkins/

## 🚀 Resumo dos Comandos Essenciais

### Para iniciar o Jenkins pela primeira vez:
```bash
# 1. Instalar e iniciar
docker run -d --name jenkins-server -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts

# 2. Aguardar inicialização
sleep 30

# 3. Obter senha inicial
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword

# 4. Acessar no navegador
# http://localhost:8080
```

### Para gerenciar o Jenkins:
```bash
# Verificar status
docker ps | grep jenkins

# Ver logs
docker logs jenkins-server

# Parar
docker stop jenkins-server

# Iniciar
docker start jenkins-server

# Reiniciar
docker restart jenkins-server
```

---
**Status**: ✅ Jenkins configurado e funcionando
**Última atualização**: 2025-10-21
