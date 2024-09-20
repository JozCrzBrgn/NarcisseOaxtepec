run:
# Ejecuta el programa
	streamlit run streamlit_app.py

cred:
# Crea las credenciales
	@py -c "from my_secrets.generate_keys import crear_credenciales; crear_credenciales()";

#? make feat BRANCH="paginacion"
feat:
# Crea una rama nueva en dev
	git checkout dev
	git pull origin dev
	git checkout -b feat/$(BRANCH) dev

#? make mdev BRANCH="paginacion"
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

#? make tag TAG="paginacion" MSG="Se crea la paginacion ordenada"
tag:
# Crea un tag
	git tag -a $(TAG) -m "$(MSG)"
	git push --tags