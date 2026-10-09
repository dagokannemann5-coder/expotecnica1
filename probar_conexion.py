from repositorio.repositorio_quiz import RepositorioQuiz

repo = RepositorioQuiz()
print("Categorías:", len(repo.obtener_categorias()))
print("Preguntas:", len(repo.listar_preguntas()))
for p in repo.obtener_preguntas_para_partida(3):
    print("-", p.texto)