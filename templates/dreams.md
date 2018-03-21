{% if data %}
{% for dream in data %}
##    {{ dream.title | e }}
ID: {{ dream.id|e }}
User:  {{ dream.user|e }}
Steps:  {{ dream.step|e }}
Likes:  {{ dream.like|e }}
{% if dream.content %}
Summary: {{ dream.content|e }}
{% endif %}
{% if dream.tags %}
Summary: {% for tag in dream.tags %}{{ tag|e }} {% endfor %}
{% endif %}
{% if dream.image %}
![](../../images/{{ uid| e }}/dreams/{{ dream.image | e }})
{% endif %}
{% endfor %}
{% endif %}