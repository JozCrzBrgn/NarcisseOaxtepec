run:
# Ejecuta el programa
	streamlit run streamlit_app.py

cred:
# Ejecuta el programa
	@py -c "from my_secrets.generate_keys import crear_credenciales; crear_credenciales()";

#? make feat BRANCH="insumos"
feat:
# Ejecuta el programa
	git checkout dev
	git pull origin dev
	git checkout -b feat/$(BRANCH) dev

#? make mdev BRANCH="insumos"
mdev:
# Ejecuta el programa
	git checkout dev
	git pull origin dev
	git merge feat/$(BRANCH)

mmain:
# Ejecuta el programa
	git checkout main
	git pull origin main
	git merge dev