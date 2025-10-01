# Trabalho-Sockets
Trabalho desenvolvido na matéria CIC4004 - Programação Concorrente, Paralela e Distribuída (Turma X)

# Projeto: Comparação de Transferência de Arquivos via TCP e UDP

## Descrição
Este projeto implementa um programa cliente-servidor em Python para realizar a transferência de um arquivo entre duas máquinas (ou na mesma máquina) utilizando sockets TCP e UDP.  

O objetivo é comparar o tempo de transmissão do mesmo arquivo utilizando os dois protocolos e registrar os resultados.  

---

## Requisitos do Trabalho
1. O arquivo a ser transferido deve ser baixado de:  
   [file_example_MP4_1920_18MG.mp4 (18 MB)](https://file-examples.com/storage/fe90bd970b68dc58f98d738/2017/04/file_example_MP4_1920_18MG.mp4)  

2. O cliente deve escolher se a transmissão ocorrerá em TCP ou UDP, a partir de um menu exibido em tela.  

3. A contabilização do tempo deve ser feita apenas na transferência efetiva do arquivo, a partir do servidor.  

4. O servidor deve retornar ao cliente o tempo gasto, e o cliente deve exibir o resultado.  

5. Os testes devem ser realizados entre máquinas distintas do laboratório, utilizando um tamanho de buffer específico.  
   - Neste projeto, foi adotado **BUFFER = 65536 bytes (64 KB)**, pois:  
     - Em TCP, permite enviar grandes blocos de dados de forma eficiente, reduzindo chamadas de sistema;  
     - Em UDP, garante que cada datagrama não ultrapasse o limite máximo teórico (64 KB), evitando erros de envio.  

6. O programa foi implementado em Python.  

7. Resultados, código-fonte e instruções estão neste repositório.  

8. Não há necessidade de implementar segurança ou múltiplas conexões simultâneas.  

9. Trabalho individual ou em duplas.  

---

## Pré-requisitos
- Python 3.10 ou superior instalado  
- Arquivo de teste: `file_example_MP4_1920_18MG.mp4` na pasta src do projeto

Verifique a instalação do Python:
```bash
python --version
````

---

## Como executar
1. Clonar o repositório
2. Executar o servidor
Na máquina que será o servidor, rode:
````bash
python server.py --host 0.0.0.0 --port 9000
````
Args:
--host 0.0.0.0 → escuta em todos os endereços de rede.
--port 9000 → porta usada para conexões.

3. Executar o cliente
Na máquina cliente, substitua IP_DO_SERVIDOR pelo IP real do servidor:
````bash
python client.py --server IP_DO_SERVIDOR --port 9000
````
4. Escolher protocolo
No menu exibido pelo cliente, digite:
1 → TCP
2 → UDP
O cliente exibirá o tempo de transmissão medido pelo servidor.

# Resultados Esperados:

**TCP** tende a ser mais confiável, garantindo entrega correta do arquivo.
**UDP** tende a ser mais rápido, mas pode sofrer com perda de pacotes.
O tempo medido pode variar dependendo da rede e das máquinas usadas.

# Testes:
1. Tempo recebido com **TCP**: 0.074279
2. Tempo recebido com **UDP**: **Não consegui realizar o teste**

Motivo dos tempos:
- A conexão no momento dos testes está oscilando muito, fazendo com que não seja possível a transmição via UDP.

