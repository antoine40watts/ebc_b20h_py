<script>
    import { apiUrl } from '../stores';
    import Accordion from './Accordion.svelte';
    import AutoComplete from "simple-svelte-autocomplete/src/SimpleAutocomplete.svelte";
    import { tooltip } from "../tooltip.js";
    import { dbAction } from '../db.js';

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

    async function getClientList(keyword) {
        const url = `${apiUrl}/get-clients?keyword=${encodeURIComponent(keyword)}`;
        const response = await fetch(url)
        const json = await response.json()

        return json
    }

    async function loadclient() {
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

        const client = await dbAction("client", "get", {"id": selectedClient.id});
        client_name = client.nom;
        client_surname = client.prenom;
        client_address = client.adresse;
        client_city = client.ville;
        client_phone = client.telephone;
        client_email = client.email;
        inputValue = selectedClient.label;
    }

    async function newClient() {
        const clientData = {
            id: 0,
            nom: client_name,
            prenom: client_surname,
            adresse: client_address,
            ville: client_city,
            telephone: client_phone,
            email: client_email,
        }

        const client = await dbAction("client", "add", clientData);
        selectedClient = {id: client.id, label: client.label};
    }

    async function updateClient() {
        const clientData = {
            nom: client_name,
            prenom: client_surname,
            adresse: client_address,
            ville: client_city,
            telephone: client_phone,
            email: client_email,
        }

        let action = "update";
        if (selectedClient) {
            clientData.id = selectedClient.id;
        } else {
            action = "add";
        }

        const client = await dbAction("client", action, clientData)
        selectedClient = {id: client.id, label: client.label};
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
        <span slot="header-search" class="search-container hide-on-print">
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
                title="Enregistrer les modifications" use:tooltip on:click={updateClient}
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
        background-color: #fffc;
        border-radius: 8px;
        /* padding: 0; */
    }

    .align-center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        /* flex-direction: column; */
    }

    @media print {
    .hide-on-print {
        display: none;
        }
    }
</style>