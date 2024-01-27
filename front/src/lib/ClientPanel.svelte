<script>

    import Accordion from './Accordion.svelte'

    export let open = false;

    let client_id = "";
    let client_name = "";
    let client_surname = "";

</script>


<Accordion bind:open={open} flex_size={1}>
    <span slot="head">Client</span>
    <div slot="details">
        <table>
            <tr>
              <td nowrap><label for="client-id">Ref. Client</label></td>
              <td><input type="text" id="client-id" name="client-id"
                bind:value={client_id}
                required minlength="4" maxlength="16" size="16"/></td>
            </tr>
            <tr>
                <td><label for="client-name">Nom</label></td>
                <td><input type="text" id="client-name" name="client-name"
                    bind:value={client_name} placeholder="non renseigné"
                    required minlength="1" maxlength="32" size="24"/></td>
                <td><label for="client-surname">Prénom</label></td>
                <td><input type="text" id="client-surname" name="client-surname"
                    bind:value={client_surname} placeholder="non renseigné"
                    required minlength="1" maxlength="32" size="24"/></td>
            </tr>
        </table>
    </div>
</Accordion>

<style>
    table td {
      height: 1.6em;
    }

    input {
        margin-left: 4px;
        margin-right: 16px;
        background-color: white;
        border-radius: 16px;
        border: 0;
    }
</style>