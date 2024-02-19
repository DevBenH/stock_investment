var investBtn = document.querySelector('.invest-button')
var modalBg = document.querySelector('.modal-bg')
var modalClose = document.querySelector('.btn-close')
var moreInfo = document.querySelector('.more-info')


investBtn.addEventListener('click', function(){
    modalBg.classList.add('bg-active');
});

moreInfo.addEventListener('click', function(){
    modalBg.classList.add('bg-active');
});

modalClose.addEventListener('click', function(){
    modalBg.classList.remove('bg-active')
})

