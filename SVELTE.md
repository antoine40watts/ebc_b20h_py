# Installation de Node.js et npm

https://deb.nodesource.com/

    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    NODE_MAJOR=20
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
    sudo apt-get update
    sudo apt-get install nodejs -y

# Initialisation de l'application SvelteKit

  npm create svelte@lastest mon_app
  cd mon_app
  npm install

# Initialisation d'une app Svelte, sans SvelteKit

  npm create vite@latest
  cd mon_app
  npm install
  
  npm run build

# Chart.js

https://github.com/SauravKanchan/svelte-chartjs

  npm i svelte-chartjs chart.js

Si problème lors de l'installation de `svelte-chartjs`, voir https://github.com/SauravKanchan/svelte-chartjs/issues/116#issuecomment-1681693028

https://marketsplash.com/tutorials/svelte/svelte-charts/

# UI components

* https://github.com/bestguy/sveltestrap


# Ressources

* https://stackoverflow.com/questions/76656259/how-do-i-route-subpages-correctly-with-fastapi
