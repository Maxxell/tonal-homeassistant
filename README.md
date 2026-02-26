# tonal-homeassistant
Home Assistant integration for Tonal to read current detailed strength scores (not just bar graphs anymore!)

This integration was inspired by and originally based on the MIT‑licensed project at https://github.com/curlrequests/toneget


What it does?

This integration connects to your tonal account (using Home Assistant configuration system for username/password) and makes 10 sensors available, one for each muscle group.  This is the stuff that shows up in your Tonal App as a bar graph, but now you can see the actual numbers for each.

How to install it?

Create a new folder under custom_components called "tonal" and put all the operative files inside (__init__.py, manifest.json,sensor.py,tonal_api.py,config_flow.py).  

2. Reboot Home Assistant.

3. Settings / Devices & services / Add integration.

Search for "Tonal Strength Scores".  That will initiate the Home Assistant configuration wizard which will ask for your tonal email and tonal account password.  If successful, it will access tonal's service and download your 10 strength scores.  

Here is a list of the sensors it creates:
            entities:
              - entity: sensor.tonal_abs_strength_score
              - entity: sensor.tonal_back_strength_score
              - entity: sensor.tonal_biceps_strength_score
              - entity: sensor.tonal_chest_strength_score
              - entity: sensor.tonal_glutes_strength_score
              - entity: sensor.tonal_hamstrings_strength_score
              - entity: sensor.tonal_obliques_strength_score
              - entity: sensor.tonal_shoulders_strength_score
              - entity: sensor.tonal_triceps_strength_score
              - entity: sensor.tonal_quads_strength_score


Dashboard Example:
  - title: Tonal Strength Scores
    path: tonal_strength
    icon: mdi:dumbbell
    type: sections
    sections:
      - type: grid
        cards:
          - type: heading
            heading: Upper Body
          - type: entity
            entity: sensor.tonal_chest_strength_score
            name: Chest
            icon: mdi:arm-flex
          - type: entity
            entity: sensor.tonal_shoulders_strength_score
            name: Shoulders
            icon: mdi:arm-flex-outline
          - type: entity
            entity: sensor.tonal_back_strength_score
            name: Back
            icon: mdi:human-back
          - type: entity
            entity: sensor.tonal_triceps_strength_score
            name: Tricep
            icon: mdi:arm-flex
          - type: entity
            name: Bicep
            icon: mdi:arm-flex
            entity: sensor.tonal_biceps_strength_score
      - type: grid
        cards:
          - type: heading
            heading: Core
          - type: entity
            entity: sensor.tonal_abs_strength_score
            name: Abs
            icon: mdi:human-handsup
          - type: entity
            entity: sensor.tonal_obliques_strength_score
            name: Oblique
            icon: mdi:human-handsup
      - type: grid
        cards:
          - type: heading
            heading: Lower Body
          - type: entity
            entity: sensor.tonal_quads_strength_score
            name: Quads
            icon: mdi:human-legs
          - type: entity
            entity: sensor.tonal_glutes_strength_score
            name: Glutes
            icon: mdi:human-female
          - type: entity
            name: Hamstring
            icon: mdi:seat-legroom-extra
            entity: sensor.tonal_hamstrings_strength_score
      - type: grid
        cards:
          - type: heading
            heading: Raw Muscle Data
          - type: entities
            title: All Tonal Sensors
            entities:
              - entity: sensor.tonal_abs_strength_score
              - entity: sensor.tonal_back_strength_score
              - entity: sensor.tonal_biceps_strength_score
              - entity: sensor.tonal_chest_strength_score
              - entity: sensor.tonal_glutes_strength_score
              - entity: sensor.tonal_hamstrings_strength_score
              - entity: sensor.tonal_obliques_strength_score
              - entity: sensor.tonal_shoulders_strength_score
              - entity: sensor.tonal_triceps_strength_score
              - entity: sensor.tonal_quads_strength_score
    cards: []

Example Script: 
Save the current scores as temporary variables
Refresh the data with Tonal
See if any values have changed
Push a notification (you should update the target here) indicating whether any scores had changed, and which ones.  

sequence:
  - variables:
      muscles:
        abs: "{{ states('sensor.tonal_abs_strength_score') | int }}"
        back: "{{ states('sensor.tonal_back_strength_score') | int }}"
        biceps: "{{ states('sensor.tonal_biceps_strength_score') | int }}"
        chest: "{{ states('sensor.tonal_chest_strength_score') | int }}"
        glutes: "{{ states('sensor.tonal_glutes_strength_score') | int }}"
        hamstrings: "{{ states('sensor.tonal_hamstrings_strength_score') | int }}"
        obliques: "{{ states('sensor.tonal_obliques_strength_score') | int }}"
        shoulders: "{{ states('sensor.tonal_shoulders_strength_score') | int }}"
        triceps: "{{ states('sensor.tonal_triceps_strength_score') | int }}"
        quads: "{{ states('sensor.tonal_quads_strength_score') | int }}"
  - target:
      entity_id:
        - sensor.tonal_abs_strength_score
        - sensor.tonal_back_strength_score
        - sensor.tonal_biceps_strength_score
        - sensor.tonal_chest_strength_score
        - sensor.tonal_glutes_strength_score
        - sensor.tonal_hamstrings_strength_score
        - sensor.tonal_obliques_strength_score
        - sensor.tonal_shoulders_strength_score
        - sensor.tonal_triceps_strength_score
        - sensor.tonal_quads_strength_score
    action: homeassistant.update_entity
  - delay: "00:00:02"
  - variables:
      changed: |
        {% set out = [] %} {% for muscle, old in muscles.items() %}
          {% set new = states('sensor.tonal_' ~ muscle ~ '_strength_score') | int %}
          {% if new != old %}
            {% set out = out + [ muscle | capitalize ~ ': ' ~ old ~ ' → ' ~ new ] %}
          {% endif %}
        {% endfor %} {{ out }}
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ changed | length > 0 }}"
        sequence:
          - data:
              title: Tonal Strength Score Update
              message: |
                The following scores changed: {{ changed | join(', ') }}
            action: notify.mobile_app
    default:
      - data:
          title: Tonal Strength Score Update
          message: |
            Sadly, no scores changed
        action: notify.mobile_app
alias: Tonal Refresh
description: ""
