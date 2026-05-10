# 0th Assignment: Test your setup
This assignment only contains a simple test task. You should use it to set up your workflow. Make sure everything works before the graded assignments will start next week. The current assignment will not be graded.

**Pay special attention to the <span style="color:red;">NOTEs</span>  shown in bold font!**

**<span style="color:red;">NOTE:</span> We recommend that you work in a Python virtual environment. Check [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) if you do not know how to set up a virtual environment.**

## 0.1: Install git
`git` is a software used in virtually every software project to track changes and versions of code across large collaborations. We will use it in this course to provide coding assignments to you, and to get the solutions back from you.

On Linux systems, `git` should already be available. If you need to install `git`, please follow the instructions here: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git.

## 0.2: Fork this repo and clone it from your own git repository
1. Click the 'fork' button on top right of the gitlab webpage of the course repo at https://git.tu-berlin.de/lis-public/ai-course-student-ss25 to create your own fork on this gitlab. Make your fork **private**.
2. Open a bash shell and navigate to a folder of your choice.
3. Clone the repo using `git clone YOURFORK`. Here, `YOURFORK` is the URL of your fork of this repo. For example, if you forked directly on this gitlab, it will look like this: `git@git.tu-berlin.de:YOUR_USER_NAME/PATH/TO/REPO.git`
```
git clone YOURFORK
```
4. `cd` into the repo folder that appeared: `cd ai-course-student-ss25`

**<span style="color:red;">NOTE:</span> Make sure that your fork is private.**

## 0.3 Give the course tutors reading access to your repo
If you are using the TU gitlab, please add the following account(s) with the role set to `Reporter`:
- auddy

If you are using github.com, please give access to the following account(s) with the role as `Collaborator`:
- sayantanauddy

**<span style="color:red;">NOTE:</span> If you do not provide us the required access rights, we will not be able to read and grade your solution.**

## 0.4 Tell us where your repo is located
Fill out the questionnaire on ISIS. The questionnaire will ask you for the following:

1. Your student ID number (Matrikelnummer)
2. Your E-Mail address
3. The SSH-URL of your repo (that's the one that starts with `git@...`), i.e. `YOURFORK`.

**<span style="color:red;">NOTE:</span> Make sure that you provide the SSH-URL and NOT the HTTPS-URL. Providing the HTTPS-URL will cause the autograding to fail for your submission.**


## 0.5: Open assignment
Throughout this course, each assignment will be given as a subfolder of `ai-course-student-ss25`. For example, the assignment subfolder for the present assignment is `00`. Inside each assignment subfolder, you will find
1. Files containing code that you **should not edit**
2. One `README.md` that explains the task
3. One single file that you should edit according to the task. For the present assignment, this file is called `solution_00.py`. For later assignments, these files will be called `solution_01.py`, `solution_02.py`, and so on. **This is the only file that should be edited**. 


**<span style="color:red;">NOTE:</span> Make sure that any code that you write is fully contained in the `solution_xx.py` file. DO NOT create any additional files.**

## 0.6: Complete assignment
Inside `solution_00.py`, there will be functions / code that you should change so that they generate the desired output.

As an example, please modify the function body of the function `is_even_and_positive(x)` so that it

- returns `True` if `x` is an even and positive integer
- returns `False` in all other cases

**<span style="color:red;">NOTE:</span> Only modify the function body and nothing else! Do not change the function name!**

**<span style="color:red;">NOTE:</span> All necessary imports will be mentioned. Do not import additional libraries!**

Of course there are many ways to solve this, but one would be to use the functions provided in `module_1.py` like this:
```python
from module_1 import is_positive, is_even # This import is already provided
```
You can test your function by changing directory to the task folder `00`, and then simply typing `python3 -m pytest`. If you haven't yet, you will need to install pytest first: `python3 -m pip install pytest`
```
cd ai-course-student-ss25/00
python3 -m pytest
```

This will run the tests defined in the file `00/tests/test_public.py`. When you hand in your solution, we will test it with a very similar `test_private.py`. This file looks very similar, we only change the input-output combinations.

## 0.7: Stage, commit, and push your solution
Once you have finished your implementation, *stage* your changes using
```
cd ai-course-student-ss25/00
git add solution_00.py
```
Then *commit* your changes using
```
git commit -m "YOUR COMMIT MESSAGE"
```
This will save your changes to `solution_00.py`. Replace `YOUR COMMIT MESSAGE` with a proper commit message.

Push your new commit to your forked repository using
```
git push
```

**<span style="color:red;">NOTE:</span> Do not push the contents of your virtual environment to your repository (use the `.gitignore` file for ignoring the virtual environment directory).**


After the assignment deadline, we will automatically evaluate your code.

## 0.8: Merge your fork of this repo after the next assignment has been published
In order to keep your own fork of this repo up-to-date with updates to the next assignments, you need to merge.

For this, first add the URL of this repository (i.e. our repository) as upstream to your fork (**you only need to do this once**):
```
git remote add upstream git@git.tu-berlin.de:lis-public/ai-course-student-ss25.git
```
By typing `git remote -v`, you can verify that there are 2 remote urls added to your fork now: The url for "origin" contains the branches of your fork, "upstream" contains the branches of this repo.

Every time you want to merge your repo with new updates on the upstream (i.e. you want to fetch the new assignments released by us), run
```
git fetch upstream
git merge upstream/main origin/main
```
`fetch` checks for new commits found at the upstream url, and `merge` merges the upstream branch (called `upstream/main`) with your branch (called `origin/main`).

If you only committed changes in `solution_xx.py`, you will be able to merge automatically (without conflicts).
