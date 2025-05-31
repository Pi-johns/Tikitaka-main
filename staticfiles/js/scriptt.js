document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.getElementById('menuButton');
    const searchButton = document.getElementById('searchButton');
    const menuPopup = document.getElementById('menuPopup');
    const searchPopup = document.getElementById('searchPopup');
    const searchCloseButton = document.getElementById('searchCloseButton');

    menuButton.addEventListener('click', () => {
        if (menuPopup.style.display === 'block') {
            menuPopup.style.display = 'none';
        } else {
            menuPopup.style.display = 'block';
            searchPopup.style.display = 'none'; // Ensure search popup is hidden
            
        }
    });

    searchButton.addEventListener('click', () => {
        if (searchPopup.style.display === 'block') {
            searchPopup.style.display = 'none';
        } else {
            searchPopup.style.display = 'block';
            menuPopup.style.display = 'none'; // Ensure menu popup is hidden
        }
    });

    searchCloseButton.addEventListener('click', () => {
        searchPopup.style.display = 'none';
    });

    document.addEventListener('click', (event) => {
        if (!menuButton.contains(event.target) && !menuPopup.contains(event.target) &&
            !searchButton.contains(event.target) && !searchPopup.contains(event.target)) {
            menuPopup.style.display = 'none';
            searchPopup.style.display = 'none';
        }
    });
});

