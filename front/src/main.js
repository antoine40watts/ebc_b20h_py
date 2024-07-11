import './app.css'
import App from './App.svelte'
import { apiUrl } from './stores';


const app = new App({
  target: document.getElementById('app'),
})

export default app;


var rpc_id = 0;

export async function makeRPCRequest(method, params) {
  const url = apiUrl + '/rpc';

  try {
      const response = await fetch(url, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
              jsonrpc: '2.0',
              method: method,
              params: params,
              id: 0,
          }),
      });

      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
          throw new Error(data.error.message);
      }

      //return JSON.stringify(data.result, null, 2);
      return data.result;
  } catch (e) {
      console.error(e.message);
      return e.message;
  }
}