document.addEventListener('DOMContentLoaded', listeners)

function listeners(){
    let input = document.getElementById('quote-search');
    let debounceTimeout = null;
    let result =  document.getElementById('result');
    let form = document.querySelector('form');

    input.addEventListener('keyup', search_get);
    form.addEventListener('submit', processForm);
    

    function searchEvents(){
        let term = input.value;
        //remove spaces from both sides
        term = term.trim();
        if (term){
            $.ajax({
            url: '/search/' + term,
            method: 'get',
            async: true, // notice this line
            })
            .done(function(search_list, status, xhr){
                // document.querySelector('#result').innerHTML = ''
                removeChart();
                document.querySelector('#search').innerHTML = search_list;
                let search_links = document.querySelectorAll('.search-container li');
                search_links.forEach(link => {
                    link.addEventListener('click', function(){
                      document.querySelector('input[name="symbol"]').value =
                        this.dataset.symbol;
                      document.querySelector('#search').innerHTML = '';
                    })
                })
            })
            .fail(function(xhr, status, error){
                    console.log(error);
            });
        }
        else{
           document.querySelector('#search').innerHTML = ''; 
        }
    }
    
    function search_get(event){
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(searchEvents, 300);
    }

    function processForm(event){
      event.preventDefault();
      let symbol = document.querySelector('input[name="symbol"]').value.toUpperCase();
      let range = document.querySelector('select[name="range"]').value;
      let route = `/chart/${symbol}/${range}`;
      fetch(route)
      .then(resp => resp.json())
      .then(chart => {
          // if the object is not null (has some enumerable properties)
          if (Object.keys(chart).length > 0 ){
            drawChart(chart);
          } 
          else {
            let modal = new Modal();
            modal.show('Sorry, this symbol is unknown!');
          }
      })
      .catch(error => {
        console.log(error);
      })
    }

    function removeChart(){
      let chart_container = document.querySelector('.chart-container');
      chart_container.innerHTML = '';
      let canvas = document.createElement('canvas');
      canvas.id = 'myChart';
      chart_container.append(canvas);
    }

    // see: https://www.chartjs.org/docs/latest/general/responsive.html (important note)
    // see: https://stackoverflow.com/questions/41958548/chartjs-change-axis-line-color
    function drawChart(chart){
      document.querySelector('#search').innerHTML = '';
      let ctx = document.getElementById('myChart');
      let myChart = new Chart(ctx,{
        type:'line',
        data:{
          labels:chart['labels'],
          datasets:[
            {
              data:chart['data'],
              label:chart['symbol'],
              fill:false,
              borderColor:"blue"
            } 
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio:false,
          scales: {
            xAxes: [{
              ticks: {
                  fontColor: "limegreen",
              },
              gridLines: {
                zeroLineColor: 'limegreen'
              }
            }],
            yAxes: [{
                ticks: {
                    fontColor: "limegreen",
                },
                gridLines: {
                  zeroLineColor: 'limegreen',
                  color: "limegreen"
                }
            }],
        }
        }
      });
    }
}