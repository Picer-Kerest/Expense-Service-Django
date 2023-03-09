const searchField = document.querySelector('#searchField');
const appTable = document.querySelector('.app-table');
const tableOutput = document.querySelector('.table-output');
const paginatorContainer = document.querySelector('.paginator-container');
const outputTableBody = document.querySelector('.output-table-body');

tableOutput.style.display = 'none';


searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    if (searchValue.trim().length > 0) {
        paginatorContainer.style.display = 'none';
        outputTableBody.innerHTML = '';
        fetch('search-expense/', {
            body: JSON.stringify({ searchText: searchValue }),
            method: 'POST'
        }).then(res => res.json())
            .then(data => {
                appTable.style.display = 'none';
                tableOutput.style.display = 'block';
                if (data.length === 0 ) {
                    tableOutput.innerHTML = 'No results found';
                } else {
                    outputTableBody.innerHTML = '';
                    data.forEach((item) => {
                        outputTableBody.innerHTML += `
                        <tr>
                            <th>${item.amount}</th>
                            <th>${item.category}</th>
                            <th>${item.description}</th>
                            <th>${item.date}</th>
                        </tr>`;
                    })
                }
            });
    } else {
        tableOutput.style.display = 'none';
        appTable.style.display = 'block';
        paginatorContainer.style.display = 'block';
    }
});

