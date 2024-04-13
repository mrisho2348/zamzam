/* tulis JS nya sendiri ya, mengikuti seperti dalam video,
selamat belajar.. ^^ */
$(document).ready(function()
{
    $("#slider-hero").owlCarousel(
        {   loop: true,
            nav: true,         
            margin:0,
            items:1,
            navText:[
                "<i class='fa fa-angle-left'></i>",
                "<i class='fa fa-angle-right'></i>",
            ],
            navContainer: "#slider-hero-nav",
        }
    );

    $("#tenaga-pendidit-slider").owlCarousel(
        {   loop: true,
            nav: true,
            dots:false,
            items:3,
            margin:30,
            navText:[
                "<i class='fa fa-angle-left'></i>",
                "<i class='fa fa-angle-right'></i>",
            ],
            navContainer: "#slider-tools-1",
        }
    );

    $('#alumni-slider').owlCarousel(
        {   loop: true,
            nav: true,
            dots:false,
            items:3,
            margin:20,
            navText:[
                '<i class="fa fa-angle-left"  aria-hidden="true"></i>',
                '<i class="fa fa-angle-right" aria-hidden="true"></i>',
            ],
            navContainer: '#slider-tools-2',
        }
    );

    $("#galeri-slider").owlCarousel(
        {   loop: true,
            nav: true,
            dots:false,
            items:3,
            margin:30,
            navText:[
                "<i class='fa fa-angle-left'></i>",
                "<i class='fa fa-angle-right'></i>",
            ],
            navContainer: "#slider-tools-3",
        }
    );

});