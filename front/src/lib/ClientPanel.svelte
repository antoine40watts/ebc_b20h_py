<script>
    import { apiUrl } from '../stores';
    import Accordion from './Accordion.svelte';
    import AutoComplete from "simple-svelte-autocomplete/src/SimpleAutocomplete.svelte";
    import { tooltip } from "../tooltip.js";

    export let open = false;

    const defaultPlaceholder = "non renseigné";
    let updateDisabled = true;
    let saveDisabled = true;
    let deleteDisabled = true;

    let client_name = "";
    let client_surname = "";
    let client_address = "";
    let client_city = "";
    let client_phone = "";
    let client_email = "";
    
    let inputValue = "";
    let selectedClient = null;

    function valueChanged() {
        if (client_name == "") {
            saveDisabled = true;
            updateDisabled = true;
        } else {
            saveDisabled = false;
            updateDisabled = false;
        }
    }


    async function loadclient() {
        console.log("load client");
        if (selectedClient == null) {
            client_name = "";
            client_surname = "";
            client_address = "";
            client_city = "";
            client_phone = "";
            client_email = "";
            inputValue = "";
            return;
        }
        
        updateDisabled = true;
        saveDisabled = true;
        deleteDisabled = false;

        const url = `${apiUrl}/get-client?id=${selectedClient.id}`;
        const response = await fetch(url);
        const client = await response.json();
        console.log(selectedClient);
        console.log(client);

        client_name = client.nom;
        client_surname = client.prenom || "";
        client_address = client.adresse || "";
        client_city = client.ville || "";
        client_phone = client.telephone || "";
        client_email = client.email || "";
        inputValue = selectedClient.label;
    }


    async function getClientList(keyword) {
        const url = `${apiUrl}/get-clients?keyword=${encodeURIComponent(keyword)}`;
        const response = await fetch(url)
        const json = await response.json()

        return json
    }

    async function newClient() {
        console.log("New Client");

        const url = `${apiUrl}/new-client`;

        const clientData = {
            client_id: 0,
            nom: client_name,
            prenom: client_surname,
            adresse: client_address,
            ville: client_city,
            phone: client_phone,
            email: client_email,
        }

        const response = await fetch(url, {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(clientData),
        });

        const json = await response.json();
        selectedClient = json;
        console.log(json);
    }

    async function updateClient() {
        console.log("Update Client");
        console.log("selected", selectedClient)

        let client_id = 0;
        let url = `${apiUrl}/update-client`;
        if (selectedClient) {
            client_id = selectedClient.id;
        } else {
            url = `${apiUrl}/new-client`;
        }

        const clientData = {
            client_id: client_id,
            nom: client_name,
            prenom: client_surname,
            adresse: client_address,
            ville: client_city,
            phone: client_phone,
            email: client_email,
        }

        const response = await fetch(url, {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(clientData),
        });

        const json = await response.json()
        selectedClient = json;
        console.log("json", json);
    }

    async function deleteClient() {
        console.log("delete client");
        if (selectedClient == null)
            return;

        const url = `${apiUrl}/delete-client?id=${selectedClient.id}`;

        const response = await fetch(url, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Resource was deleted successfully
            // You can optionally handle the response data here
            console.log("Client deleted");
            selectedClient = null;
        } else {
            // DELETE request failed
            // You can handle the error here
            console.error("Client not deleted");
        }
    }
</script>


<Accordion bind:open={open} flex_size={1}>
    <span slot="header-icon"><i class="fa-regular fa-user"></i></span>
    <span slot="header-title">Client</span>
        <span slot="header-search" id="search-container">
            <AutoComplete
                searchFunction={getClientList}
                delay=200
                localFiltering={false}
                labelFieldName="label"
                valueFieldName="id"
                bind:selectedItem={selectedClient}
                bind:text={inputValue}
                onChange={loadclient}
                loadingText="Chargement..."
                noResultsText="Aucun résultat"
                placeholder="Rechercher"
            />
        </span>
    <div class="align-center" slot="details">
        <table style="width:max-content">
            <tr>
                <td><label for="client-name">Nom</label></td>
                <td><input type="text" id="client-name" name="client-name"
                    bind:value={client_name} placeholder={defaultPlaceholder}
                    on:input={valueChanged}
                    required minlength="1" maxlength="32" size="24"/></td>
                <td><label for="client-surname">Prénom</label></td>
                <td><input type="text" id="client-surname" name="client-surname"
                    bind:value={client_surname} placeholder={defaultPlaceholder}
                    on:input={valueChanged}
                    minlength="1" maxlength="32" size="24"/></td>
            </tr>
            <tr>
                <td><label for="client-address">Adresse</label></td>
                <td><input type="text" id="client-address" name="client-address"
                    bind:value={client_address} placeholder={defaultPlaceholder}
                    on:input={valueChanged}
                    minlength="1" maxlength="32" size="24"/></td>
                <td><label for="client-city">Ville</label></td>
                <td><input type="text" id="client-city" name="client-city"
                    bind:value={client_city} placeholder={defaultPlaceholder}
                    on:input={valueChanged}
                    minlength="1" maxlength="32" size="24"/></td>
            </tr>
            <tr>
                <td><label for="client-phone">Téléphone</label></td>
                <td><input type="text" id="client-phone" name="client-phone"
                    bind:value={client_phone} placeholder="0000000000"
                    on:input={valueChanged}
                    minlength="1" maxlength="13" size="16"/></td>
                <td><label for="client-email">E-mail</label></td>
                <td><input type="text" id="client-email" name="client-email"
                    bind:value={client_email} placeholder="{defaultPlaceholder}"
                    on:input={valueChanged}
                    minlength="1" maxlength="32" size="24"/></td>
            </tr>
        </table>
        <div>
            <button
                class="btn-add-db" on:click={newClient}
                title="Créer un nouveau client" use:tooltip
                disabled={saveDisabled} >
                <i class="fa-solid fa-circle-plus"></i>
            </button>
            <button class="btn-update-client"
                title="Modifier la fiche client" use:tooltip on:click={updateClient}
                disabled={updateDisabled} >
                <i class="fa-solid fa-floppy-disk"></i>
            </button>
            <button class="btn-delete-client"
                title="Supprimer le client" use:tooltip on:click={deleteClient}
                disabled={deleteDisabled} >
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
    </div>
</Accordion>


<style>
    table td {
      height: 1.6em;
    }

    input {
        margin-left: 4px;
        margin-right: 16px;
        background-color: #fffa;
        border-radius: 16px;
        border: 0;
    }

    button {
        width: 34px;
        height: 34px;
        font-size: 1em;
        /* margin: 2px; */
        padding: 4px;
    }

    :global(.autocomplete) {
        font-weight: 400;
        height: 1em;
    }

    :global(.autocomplete-input) {
        background-color: #fffd;
        border: none;
        border-radius: 8px;
        padding: 0;
        height: 10px;
    }

    .align-center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        /* flex-direction: column; */
    }
</style>