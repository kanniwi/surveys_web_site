document.addEventListener("DOMContentLoaded", function () {
    console.log("Survey data:", surveyData); // Debug log

    const colors = ['#f28b82', '#fbbc04', '#34a853', '#4285f4', '#a142f4', '#ff6d01', '#46bdc6'];

    surveyData.questions.forEach(question => {
        console.log("Processing question:", question); // Debug log

        const pieCanvas = document.getElementById("pie_chart_" + question.id);
        console.log("Pie canvas found:", !!pieCanvas); // Debug log

        let labels = [];
        let data = [];

        if (question.type === 'text') {
            labels = question.text_responses.map(stat => stat.text);
            data = question.text_responses.map(stat => stat.count);
        } else {
            labels = question.options.map(option => option.text);
            data = question.options.map(option => option.vote_count || 0);
        }

        console.log("Labels:", labels); // Debug log
        console.log("Data:", data); // Debug log

        if (pieCanvas && labels.length && data.reduce((a, b) => a + b, 0) > 0) {
            try {
                new Chart(pieCanvas, {
                    type: "pie",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Ответы",
                            data: data,
                            backgroundColor: colors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { 
                            legend: { 
                                position: 'bottom',
                                labels: {
                                    font: {
                                        size: 12
                                    }
                                }
                            } 
                        }
                    }
                });
                console.log("Pie chart created successfully"); // Debug log
            } catch (error) {
                console.error("Error creating pie chart:", error); // Debug log
            }
        }

        if (question.type !== 'text') {
            const barCanvas = document.getElementById("bar_chart_" + question.id);
            console.log("Bar canvas found:", !!barCanvas); // Debug log

            if (barCanvas) {
                try {
                    new Chart(barCanvas, {
                        type: "bar",
                        data: {
                            labels: labels,
                            datasets: [
                                {
                                    label: "Мужчины",
                                    data: question.options.map(option => option.gender_counts.male),
                                    backgroundColor: "#4285f4"
                                },
                                {
                                    label: "Женщины",
                                    data: question.options.map(option => option.gender_counts.female),
                                    backgroundColor: "#f28b82"
                                },
                                {
                                    label: "Не указано",
                                    data: question.options.map(option => option.gender_counts.not_s),
                                    backgroundColor: "#a142f4"
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { 
                                    position: "bottom",
                                    labels: {
                                        font: {
                                            size: 12
                                        }
                                    }
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function (context) {
                                            return context.dataset.label + ": " + context.parsed.y;
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: { 
                                        display: true, 
                                        text: "Количество ответов",
                                        font: {
                                            size: 12
                                        }
                                    }
                                }
                            }
                        }
                    });
                    console.log("Bar chart created successfully"); // Debug log
                } catch (error) {
                    console.error("Error creating bar chart:", error); // Debug log
                }
            }
        }
    });
});
