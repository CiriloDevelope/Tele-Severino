# ============================================================
# DADOS MOCKADOS DO PROTÓTIPO
# ============================================================
# Estes dados simulam o retorno do backend/banco.
# Depois, os repositories devem buscar essas informações no PostgreSQL.
# ============================================================

CATEGORIES = [
    {"slug": "eletrica", "name": "Elétrica", "icon": "⚡", "tone": "yellow"},
    {"slug": "tecnologia", "name": "Tecnologia", "icon": "◌", "tone": "blue"},
    {"slug": "construcao", "name": "Construção", "icon": "⌁", "tone": "orange"},
    {"slug": "culinaria", "name": "Culinária", "icon": "✂", "tone": "red"},
    {"slug": "estudos", "name": "Estudos", "icon": "□", "tone": "green"},
    {"slug": "design", "name": "Design", "icon": "◉", "tone": "purple"},
]

SPECIALISTS = [
    {
        "id": 1,
        "name": "Ana Souza",
        "role": "Desenvolvedora",
        "category": "tecnologia",
        "rating": "4.9",
        "reviews": 203,
        "price": "5.00",
        "about": "Desenvolvedora full-stack com 10 anos de experiência. Especialista em React, Node.js e soluções em nuvem.",
        "tags": ["Desenvolvimento web", "React e Node.js", "Cloud computing", "Arquitetura de software"],
        "initials": "AS",
        "avatar_class": "avatar-1",
    },
    {
        "id": 2,
        "name": "Rafael Lima",
        "role": "Infraestrutura",
        "category": "tecnologia",
        "rating": "4.8",
        "reviews": 156,
        "price": "4.80",
        "about": "Especialista em redes, servidores, cloud e suporte para pequenas empresas.",
        "tags": ["Redes", "Servidores", "Cloud", "DevOps"],
        "initials": "RL",
        "avatar_class": "avatar-2",
    },
    {
        "id": 3,
        "name": "Carlos Mendes",
        "role": "Suporte Técnico",
        "category": "tecnologia",
        "rating": "4.7",
        "reviews": 189,
        "price": "3.80",
        "about": "Atendimento técnico rápido para computadores, sistemas e dúvidas digitais.",
        "tags": ["Suporte técnico", "Windows", "Hardware"],
        "initials": "CM",
        "avatar_class": "avatar-3",
    },
    {
        "id": 7,
        "name": "Pedro Santos",
        "role": "Engenheiro Civil",
        "category": "construcao",
        "rating": "4.9",
        "reviews": 156,
        "price": "4.00",
        "about": "Consultoria para pequenas obras, reformas e dúvidas estruturais.",
        "tags": ["Construção", "Reforma", "Obra residencial"],
        "initials": "PS",
        "avatar_class": "avatar-7",
    },
]
