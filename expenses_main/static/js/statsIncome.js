const renderChart = (data, labels) => {
    const ctx = document.getElementById('myChart');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Last 6 months incomes',
                data: data,
                  backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 206, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(255, 159, 64, 0.2)",
                  ],
                  borderColor: [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)",
                  ],
                  borderWidth: 1,
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Incomes per category'
            }
        }
    });
}

const getChartData = () => {
    fetch('/income/income-category-summary/')
        .then(res => res.json())
        .then(results => {
            console.log(results);
            const source_data = results.income_source_data;
            const [data, labels] = [Object.values(source_data), Object.keys(source_data)];
            renderChart(data, labels);
        });
}

document.onload = getChartData();
// document.onload - это событие, которое происходит, когда веб-страница полностью загружена в браузере.
// Это означает, что все элементы на странице, такие как изображения, стили, скрипты, видео и т. д., загружены и готовы к использованию.
