run:
# Ejecuta el programa
	streamlit run inventario.py

cred:
# Crea las credenciales
	@py -c "from my_secrets.generate_keys import crear_credenciales; crear_credenciales()";

#? make feat BRANCH="insumos"
feat:
# Crea una rama nueva en dev
	git checkout dev
	git pull origin dev
	git checkout -b feat/$(BRANCH) dev

#? make mdev BRANCH="insumos"
mdev:
# Hace un merge en la rama dev
	git checkout dev
	git pull origin dev
	git merge feat/$(BRANCH)

mmain:
# Hace un merge en la rama main
	git checkout main
	git pull origin main
	git merge dev

#? make tag TAG="insumos" MSG="Se crea pagina de insumos"
tag:
# Crea un tag
	git tag -a $(TAG) -m "$(MSG)"
	git push --tags