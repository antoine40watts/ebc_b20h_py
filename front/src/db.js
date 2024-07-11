import { apiUrl } from "./stores";

export async function dbAction(tablename, action, params) {
    console.log("DB ACTION", tablename, action, params);

    const data = {
        table_name: tablename,
        action: action,
        params: params,
    }

    const url = `${apiUrl}/db-action/`;
    const response = await fetch(url, {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data),
    });
    const responseData = await response.json();
    console.log("response:", responseData);
    return responseData;
}