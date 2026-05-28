#CRIAÇÃO DO BANCO DE DADOS
create database tele_severino;

use tele_severino;

#1. TABELA DE USUÁRIOS (BASE)
create table usuarios (
id_usuario int primary key auto_increment,
nome varchar(100) not null,
email varchar(100) unique not null,
tipo enum( 'CLIENTE', 'ESPECIALISTA') not null,
data_criacao timestamp default current_timestamp
);

#2. TABELA DE ESPECIALISTAS (DETALHES DOS PROFISSIONAIS)
create table especialistas (
id_especialista int primary key,
valor_minuto decimal(10,2) not null,
especialista varchar(50),
foreign key (id_especialista) references usuarios(id_usuario)
);

#3 TABELA DE CATEGORIAS
create table categorias(
id_categoria int primary key auto_increment,
nome_categoria varchar(50) not null
);

#4. TABELA DE CONSULTORIAS (SESSÕES)
create table consultorias (
id_consultoria int primary key auto_increment,
id_cliente int,
id_especialista int,
id_categoria int,
inicio_sessao datetime,
fim_sessao datetime,
valor_total decimal(10,2),
foreign key (id_cliente) references usuarios(id_usuario),
foreign key (id_especialista) references especialistas(id_especialista),
foreign key (id_categoria) references categorias(id_categoria)
);

#5. TABELA AVALIAÇÕES
create table avaliacoes (
id_avaliacao int primary key auto_increment,
id_consultoria int,
nota int check (nota between 1 and 5),
comentario text,
foreign key (id_consultoria) references consultorias(id_consultoria)
);
