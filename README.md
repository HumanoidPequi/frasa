## marta_simulation

Este repositório fornece um ambiente de desenvolvimento voltado para simulações usando Gazebo com modelos e mundos customizados para o robo humanoid Martha.

## Índice

- [Simulação da Martha](#marta_simulation)
  - [Índice](#Índice)
  - [Introdução](#Introdução)
  - [Estrutura do Repositório](#estrutura-do-repositório)
  - [Requisitos](#requisitos)
  - [Getting Started](#getting-started)
    - [Clonando o Repositório e Compilando o Workspace nativo](#clonando-o-repositório-e-compilando-o-workspace-nativo)
    - [Clonando o Repositório e Compilando o Workspace via docker](#clonando-o-repositório-e-compilando-o-workspace-via-docker)
  - [Executando a simulação](#executando-a-simulação)
  - [Contribuindo](#Contribuindo)

## Introdução
Este projeto foi desenvolvido para fornecer um ambiente pronto para desenvolvimento e teste de simulações com a Martha no Gazebo utilizando ROS Noetic. O ambiente inclui todas as dependências necessárias, modelos personalizados e mundos de simulação para simplificar o fluxo de desenvolvimento.

## Estrutura do Repositório

- **docker/**: Contem arquivo de imagem Docker
- **Martha_ws/**: Workspace para simulação da Martha

## Requisitos

- Docker (opcional)
- Ubuntu 20.04
- Ros Noetic
- Gazebo-Classic
- ros_control

## Getting Started

### Clonando o Repositório e Compilando o Workspace nativo

Para clonar o Workspace execute
`git clone git@github.com:HumanoidPequi/marta_simulation.git`

Para compilar o workspace, dentro do repositorio marta_simulation acesse o diretorio Martha_ws e execute o build do workspace da seguinte forma:

```
//dentro do repositorio 
cd Martha_ws
catkin_make
```

Apos isso, execute o source do workspace
```
//dentro de Martha_ws
source devel/setup.bash
```

### Clonando o Repositório e Compilando o Workspace via docker

Dentro da raiz do repositorio, realize a build da imagem docker

`docker build docker -t martha_sim:1.0`

Dentro da imagem docker execute a simulação


## Executando a simulação

Para executar a simulação, tanto docker quanto nativo, execute
`roslaunch martha_gazebo gazebo.launch`

## Contribuindo

Contribuições são bem-vindas! Por favor, envie um pull request ou abra uma issue se você encontrar problemas ou tiver sugestões para melhorias.