const form1 = document.querySelector("#create_game_input");
const form2 = document.querySelector("#join_game_input");

function handler(evt) {
	// verhindere Standardverhalten des Formulars
	evt.preventDefault();

	// holt die input Elemente
	const inputs = evt.target.querySelectorAll("input");

	// extrahiert die Daten
	const data = Array.from(inputs).map((input) => [input.id, input.value]);

	// logt die Daten in der Console des Browsers.
	console.log(data);
}

form1.addEventListener("submit", handler);
form2.addEventListener("submit", handler);
