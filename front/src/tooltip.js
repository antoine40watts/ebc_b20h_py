export function tooltip(element) {
	let div;
	let title_backup;

	function mouseOver(event) {
		// NOTE: remove the `title` attribute, to prevent showing the default browser tooltip
		// remember to set it back on `mouseleave`
		
		let title = element.getAttribute('title');
		if (title == null)
			return;
		title_backup = title;

		element.removeAttribute('title');
		
		div = document.createElement('div');
		div.textContent = title;
		div.style = `
			border: 1px solid #ddd;
			box-shadow: 1px 1px 1px #ddd;
			background: white;
			border-radius: 4px;
			padding: 4px;
			position: absolute;
			top: ${event.pageX + 5}px;
			left: ${event.pageY + 5}px;
		`;
		document.body.appendChild(div);
	}

	function mouseMove(event) {
		div.style.left = `${event.pageX + 5}px`;
		div.style.top = `${event.pageY + 5}px`;
	}

	function mouseLeave() {
		document.body.removeChild(div);
		// NOTE: restore the `title` attribute
		element.setAttribute('title', title_backup);
	}
	
	element.addEventListener('mouseover', mouseOver);
  	element.addEventListener('mouseleave', mouseLeave);
	element.addEventListener('mousemove', mouseMove);
	
	return {
		destroy() {
			element.removeEventListener('mouseover', mouseOver);
			element.removeEventListener('mouseleave', mouseLeave);
			element.removeEventListener('mousemove', mouseMove);
			if (document.contains(div)) {
				div.remove();
			}
		}
	}
}