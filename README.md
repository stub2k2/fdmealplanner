# fdmealplanner for Homeassistant

Place fdmealplanner/ directory inside /config/custom_components/

In your /config/configuration.yaml add a block under sensors:

```
- platform: fdmealplanner
  accounts:
    - 'XX/YY/Z'
```      
      
`/XX/YY/Z` is the codes in the FD MealPanner URL: https://classic.fdmealplanner.com/ for your school and meal type. For instance if you choose "Huntington Washington"  and the lunch meal, the URL you will be taken to is: `https://classic.fdmealplanner.com/#menu/mealPlanner/27/65/2` so use `27/65/2` for your code.

This will create a sensor called sensor.fdmealplanner_27_65_2 with attributes of lunch0, lunch1, lunch2, lunch3, lunch4 which are the lunches of today - five days from now.
Multiple schools should work, but not tested.

This code works for me, but may need to be changed if your school is more complicated. My school has lots of items on the menu, so line 119 in sensor.py truncates to 7 items. Change it to whatever you want.

I am using a markdown card to display the first 3 entries.

```
type: markdown
content: |-
  {{ states.sensor.fdmealplanner_27_65_2.attributes.lunch0 }}
  {{ states.sensor.fdmealplanner_27_65_2.attributes.lunch1 }}
  {{ states.sensor.fdmealplanner_27_65_2.attributes.lunch2 }}
title: School Lunch

```
Let me know if have any suggestions. Right now I leave the entry blank if no information. Each school gets updated once every 6 hours. 
