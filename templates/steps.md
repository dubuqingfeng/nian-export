{% if data %}
{% for step in data %}
## ID:       {{ step.sid|e }}
### Content:
```
{{ step.content | e }}
```
{% if step.image %}
![](../../images/{{ uid| e }}/steps/{{ step.dream | e }}/{{ step.sid | e }}/{{ step.image | e }})
{% endif %}
### Lastdate:  {{ step.publish_date|e }}
{% if step.likes != "0" %}
### Likes: {{ step.likes | e }}
{% endif %}
{% if step.images %}
### Images:
{% for item in step.images %}
![](../../images/{{ uid| e }}/steps/{{ step.dream | e }}/{{ step.sid | e }}/{{ item.path | e }})
{% endfor %}
{% endif %}
{% if step.step_comments %}
### Comments:
{% for item in step.step_comments %}
#### Content: {{ item.content | e }}
#### User: {{ item.user | e }}
#### Lastdate:  {{ item.publish_date|e }}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}