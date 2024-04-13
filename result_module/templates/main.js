const chart = document.querySelector("#chart").getContext("2d");

// create  a new chart instance 

new Chart(chart,
    {
       type: 'line',
       data: {
        labels: ["January", "February", "March","Apr","May","Jun","Aug","Sep","Oct","Nov"],
        datasets:[
            {
            label: 'BTC',
            data :[29921,33212,44113,44551,88114,66224,88114,66441,11552,77114,77331,55223],
            borderColor:'red',
            borderWidth: 2
        },
            {
            label: 'ETC',
            data :[51921,61212,77113,36551,88114,66266,88191,77441,22552,61114,44331,22223],
            borderColor:'blue',
            borderWidth: 2
        },
    ]
    },
       options: {
        responsive:true
       }
    }
)

// show or hide sidebar 

const menuBtn = document.querySelector('#menu-btn');
const closeBtn = document.querySelector('#close-btn');
const sidebar = document.querySelector('aside');

menuBtn.addEventListener('click', () => {
    sidebar.style.display = 'block';
})

closeBtn.addEventListener('click', () => {
    sidebar.style.display = 'none';
})

// change theme 
const themeBtn = document.querySelector('.theme-btn');

themeBtn.addEventListener('click',() => {
    document.body.classList.toggle('dark-theme');
    themeBtn.querySelector('span:first-child').classList.toggle('active');
    themeBtn.querySelector('span:last-child').classList.toggle('active');
})