# blog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Blog, Comment, CommentLike
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog_list.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.comments.filter(parent=None).order_by('-created_at')
    related_posts = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:2]

    # 🛠 Prepare likes and dislikes counts for each comment
    for comment in comments:
        comment.likes_count = comment.likes.filter(is_like=True).count()
        comment.dislikes_count = comment.likes.filter(is_like=False).count()

        # 🛠 Also for replies (child comments)
        replies = comment.replies.all()
        for reply in replies:
            reply.likes_count = reply.likes.filter(is_like=True).count()
            reply.dislikes_count = reply.likes.filter(is_like=False).count()

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'related_posts': related_posts
    })

    
@login_required
@require_POST
def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')
    parent = None
    if parent_id:
        parent = Comment.objects.get(id=parent_id)
    Comment.objects.create(blog=blog, user=request.user, content=content, parent=parent)
    return redirect(reverse('blog_detail', kwargs={'slug': slug}))

@login_required
@require_POST
def like_comment(request):
    comment_id = request.POST.get('comment_id')
    action = request.POST.get('action')  # 'up' or 'down'

    comment = get_object_or_404(Comment, id=comment_id)

    is_like = True if action == 'up' else False

    like_obj, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    like_obj.is_like = is_like
    like_obj.save()

    likes_count = comment.likes.filter(is_like=True).count()
    dislikes_count = comment.likes.filter(is_like=False).count()

    return JsonResponse({'likes': likes_count, 'dislikes': dislikes_count})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('blog_detail', pk=comment.blog.pk)

    return JsonResponse({'error': 'Invalid request'}, status=400)
