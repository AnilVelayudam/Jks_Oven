// PRICE UPDATE
const basePrices = window.basePrices || {};

function updatePrice(){
    let cream = document.querySelector('input[name="cream"]:checked').value;
    let weight = parseFloat(document.querySelector('input[name="weight"]:checked').value);

    let basePrice = basePrices[cream];

    if(basePrice === null){
        document.getElementById("price").innerText = "Not Available";
        return;
    }

    let finalPrice = basePrice * weight;
    document.getElementById("price").innerText = "₹" + finalPrice;
}


// INIT
document.addEventListener("DOMContentLoaded", function(){

updatePrice();

document.querySelectorAll('input[name="cream"], input[name="weight"]').forEach(el => {
    el.addEventListener("change", updatePrice);
});

});


// ADD TO CART
function addToCart(){
    let cream = document.querySelector('input[name="cream"]:checked').value;
    let weight = document.querySelector('input[name="weight"]:checked').value;

    window.location.href = `/add-to-cart/${window.productId}/?cream=${cream}&weight=${weight}`;
}


// ORDER NOW
function orderNow(){
    let cream = document.querySelector('input[name="cream"]:checked').value;
    let weight = document.querySelector('input[name="weight"]:checked').value;

    window.location.href = `/buy-now/${window.productId}/?cream=${cream}&weight=${weight}`;
}


// IMAGE SWITCH
function changeImage(el){
    const main = document.getElementById("mainImage");
    main.src = el.src;

    document.querySelectorAll('.thumbnail-container img').forEach(img => {
        img.classList.remove('active');
    });

    el.classList.add('active');
}