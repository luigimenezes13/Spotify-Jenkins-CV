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

#### 4.2 Configurar Git Global (IMPORTANTE!)

**⚠️ ANTES de configurar o Pipeline, configure o Git globalmente:**

1. Vá em: **Manage Jenkins** → **Tools** (ou **Global Tool Configuration**)
2. Encontre a seção **"Git"**
3. Clique em **"Add Git"**
4. **IMPORTANTE**: Deixe o campo **"Path to Git executable"** **VAZIO** (isso fará o Jenkins usar o Git padrão do container Docker)
5. Clique em **"Save"**

**Por que isso é importante?**  
O Jenkins pode tentar usar o Git do Windows (`C:\Program Files\Git\cmd\git.exe`) dentro do container Docker Linux, o que causa erro. Deixar o campo vazio faz o Jenkins usar o Git instalado no container (`/usr/bin/git`).

#### 4.3 Configurar Pipeline
1. Na seção "Pipeline":
   - **Definition**: "Pipeline script from SCM"
   - **SCM**: Git
   - **Repository URL**: `https://github.com/luigimenezes13/Spotify-Jenkins-CV.git`
   - **Credentials**: Deixe vazio (para repositório público) ou configure credenciais se for privado
   - **Branch**: `*/main` ou `*/master` (dependendo da sua branch principal)
   - **Script Path**: `server/Jenkinsfile`
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

### Erro: "Failed to connect to repository" com Git do Windows

**Erro:**
```
Failed to connect to repository : Error performing git command: 
C:\Program Files\Git\cmd\git.exe ls-remote -h https://github.com/...
```

**Solução:**
1. Vá em: **Manage Jenkins** → **Tools** (ou **Global Tool Configuration**)
2. Encontre a seção **"Git"**
3. Clique em **"Add Git"** ou edite a configuração existente
4. **IMPORTANTE**: Deixe o campo **"Path to Git executable"** **VAZIO**
5. Clique em **"Save"**
6. Reconfigure o pipeline novamente

**Por que isso acontece?**  
O Jenkins está tentando usar o Git do Windows dentro do container Docker Linux. Deixar o campo vazio faz o Jenkins usar o Git instalado no container (`/usr/bin/git`).

**Verificação:**
```bash
# Testar Git dentro do container
docker exec jenkins-server git --version
docker exec jenkins-server git ls-remote -h https://github.com/luigimenezes13/Spotify-Jenkins-CV.git HEAD
```

### Jenkins não inicia
```bash
# Reiniciar container
docker restart jenkins-server

# Verificar logs
docker logs jenkins-server -f
```

### Pipeline falha
1. Verificar se Node.js 20 está disponível (o pipeline instala via nvm)
2. Verificar se dependências estão instaladas
3. Verificar permissões de arquivo
4. Verificar logs do build

### Problemas de Porta
```bash
# Verificar portas em uso (Windows PowerShell)
netstat -ano | findstr :8080
netstat -ano | findstr :50000

# Parar processo se necessário (substitua PID pelo número do processo)
taskkill /PID <PID> /F
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

## 🔄 Configurar Build Automático

### Opção 1: Polling (Já configurado no Jenkinsfile)

O Jenkinsfile já está configurado com polling que verifica mudanças a cada 5 minutos:
```groovy
triggers {
    pollSCM('H/5 * * * *')
}
```

**Como funciona:**
- O Jenkins verifica o repositório a cada 5 minutos
- Se houver mudanças, executa o pipeline automaticamente
- **Vantagem**: Simples, não precisa configuração adicional
- **Desvantagem**: Pode haver delay de até 5 minutos

**Após fazer commit e push:**
1. Faça commit das mudanças: `git commit -am "Atualizar código"`
2. Faça push: `git push origin main`
3. Aguarde até 5 minutos - o Jenkins executará automaticamente

**Como verificar se está funcionando:**
1. Acesse: http://localhost:8080/job/spotify-jenkins-cv/
2. Verifique o histórico de builds (história à esquerda)
3. Veja a coluna "Commit" - deve mostrar o commit mais recente
4. Se houver um novo build, clique nele para ver os logs
5. Verifique os logs para confirmar que detectou o commit

**⚠️ IMPORTANTE - Poll SCM Pode Precisar Ser Habilitado Manualmente:**
O `pollSCM` no Jenkinsfile pode não ser aplicado automaticamente. Você precisa habilitar manualmente no Jenkins UI:

1. Acesse: `spotify-jenkins-cv` → **Configure**
2. Seção **"Build Triggers"** → ✅ **Marque "Poll SCM"**
3. Schedule: `H/5 * * * *`
4. Clique em **"Save"**

**Verifique após configurar:**
- Vá em **"View Polling Log"** ou **"GitHub Hook Log"**
- Deve mostrar logs de polling sendo executado

**Teste rápido:**
```bash
# 1. Fazer um pequeno commit de teste
echo "# Teste" >> server/.test-jenkins
git add server/.test-jenkins
git commit -m "test: verificar build automático do Jenkins"
git push origin main

# 2. Aguardar até 5 minutos

# 3. Verificar no Jenkins UI se novo build foi criado
# ou verificar logs:
docker logs jenkins-server 2>&1 | grep -i "poll\|scm\|checkout\|trigger" | tail -10
```

### Opção 2: GitHub Webhooks (Recomendado - Mais Rápido)

Para builds instantâneos ao fazer push, configure webhooks:

#### 2.1 Configurar no Jenkins

1. **Instalar Plugin GitHub** (se ainda não tiver):
   - Jenkins → Manage Jenkins → Manage Plugins
   - Aba "Available"
   - Busque "GitHub plugin"
   - Instale e reinicie

2. **Configurar o Job:**
   - Vá em: `spotify-jenkins-cv` → Configure
   - Na seção "Build Triggers":
     - ✅ Marque "GitHub hook trigger for GITScm polling"
   - Salve

#### 2.2 Configurar no GitHub

1. Acesse seu repositório no GitHub
2. Vá em: **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `http://SEU_IP_JENKINS:8080/github-webhook/`
     - Se Jenkins estiver local: `http://localhost:8080/github-webhook/` (não funciona do GitHub)
     - Se Jenkins estiver em servidor público: `http://seu-ip-publico:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Selecione "Just the push event"
   - ✅ Active
4. Clique em "Add webhook"

#### 2.3 Tornar Jenkins Acessível (se necessário)

Se o Jenkins estiver rodando localmente, o GitHub não conseguirá acessá-lo. Opções:

**A) Usar ngrok (para testes):**
```bash
# Instalar ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Criar tunnel
ngrok http 8080

# Use a URL do ngrok no webhook do GitHub
# Exemplo: https://abc123.ngrok.io/github-webhook/
```

**B) Usar Polling (mais simples para desenvolvimento local):**
- O polling já está configurado no Jenkinsfile
- Funciona sem configuração adicional
- Delay máximo de 5 minutos

### Comparação das Opções

| Método | Velocidade | Configuração | Recomendado Para |
|--------|-----------|--------------|------------------|
| **Polling** | ~5 min delay | ✅ Já configurado | Desenvolvimento local |
| **Webhook** | Instantâneo | ⚠️ Requer setup | Produção/Servidor público |

## 🎯 Próximos Passos

1. ✅ **Build Automático** - Configurado com polling
2. **Configurar Deploy** para staging/produção
3. **Adicionar Notificações** (email, Slack)
4. **Configurar Backup** dos dados do Jenkins

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
