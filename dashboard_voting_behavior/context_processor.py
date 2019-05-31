def global_context(request):
    # cateogries = Category.objects.all()
    context = {'voting_id': 5,
               'vote_types': ['Ja', 'Nein','Enthalten', 'Nicht abg.', 'Nicht abg.(Gesetzlicher Mutterschutz)'],
    }
    return context
