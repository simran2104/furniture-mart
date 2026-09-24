const verifiedFurnitureImage = 'https://images.pexels.com/photos/7166647/pexels-photo-7166647.jpeg?auto=compress&cs=tinysrgb&w=1200';

document.querySelectorAll('.hero-art-label').forEach((label) => label.remove());

document.addEventListener('error', (event) => {
	const image = event.target;
	if (image.tagName !== 'IMG' || image.dataset.fallbackApplied) return;
	image.dataset.fallbackApplied = 'true';
	if (image.closest('.product-thumbnails')) {
		image.closest('button').remove();
		return;
	}
	image.src = verifiedFurnitureImage;
}, true);

document.querySelectorAll('[data-track]').forEach((element) => element.addEventListener('click', () => fetch('/api/analytics/events/', {method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken':document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''}, body: JSON.stringify({event: element.dataset.track, productId: element.dataset.productId || null})})));
