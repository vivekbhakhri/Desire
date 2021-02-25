import { CountUp } from 'https://cdnjs.cloudflare.com/ajax/libs/countup.js/2.0.7/countUp.js';

function countStart() {
  const $counters = document.querySelectorAll(".js-count-up"),
  options = {
    useEasing: true,
    useGrouping: true,
    separator: ",",
    decimal: "." };


  $counters.forEach(item => {
    const value = item.dataset.value;
    const counter = new CountUp(item, value, options);
    counter.start();
  });
}

new Waypoint({
  element: document.querySelector('.level'),
  handler: function () {
    countStart();
    //this.destroy() //for once
  },
  offset: '50%' });