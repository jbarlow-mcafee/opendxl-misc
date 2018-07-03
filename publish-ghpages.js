#!/usr/bin/env node

'use strict'

var childProcess = require('child_process')
var fs = require('fs')
var rimraf = require('rimraf')

var GH_PAGES_BRANCH = 'gh-pages'
var GH_PAGES_DIR = 'out'

var originalDir = process.cwd()

function shutdown (exitCode) {
  exitCode = exitCode || 0
  process.chdir(originalDir)
  process.exit(exitCode)
}

function runCommand (prog, args, exitMessage) {
  var proc = childProcess.spawnSync(prog, args)
  var output = proc.stdout.toString().trim()
  var exitCode = proc.status
  if (exitMessage && exitCode) {
    if (output) {
      console.log(output)
    }
    var err = proc.stderr.toString().trim()
    if (err) {
      console.log(err)
    }
    console.log(exitMessage + ', aborting...')
    shutdown(exitCode)
  }
  return {
    exitCode: proc.status,
    output: output
  }
}

function runGitCommand (args, exitMessage) {
  return runCommand('git', args, exitMessage)
}

function stagedChangesInRepo (exitMessage) {
  return runGitCommand(['diff-index', '--exit-code', '--cached', 'HEAD', '--'],
    exitMessage)
}

function main () {
  var remote = process.argv.length > 2 ? process.argv[2] : 'origin'

  runGitCommand(['status'], 'Unable to determine git repo status')

  if (!fs.existsSync('package.json')) {
    console.log(
      'Unable to locate package.json file. This may not be a Node.js project.')
    shutdown(1)
  }

  var originalCommitSha = runGitCommand(['rev-parse', 'HEAD'],
    "Can't get current git commit").output

  var refResult = runGitCommand(['symbolic-ref', '-q', 'HEAD'])
  var originalRef = refResult.exitCode ? originalCommitSha : refResult.output.replace('refs/heads/', '')

  console.log('Validating that no git repo changes are outstanding...')
  stagedChangesInRepo('Staged changes in git repo')
  runGitCommand(['diff-files', '--exit-code'], 'Unstaged changed in git repo')

  var ghPagesBranchUpToDate = false

  console.log('Setting up ' + GH_PAGES_BRANCH + ' branch...')
  if (runGitCommand(['rev-parse', '--quiet',
    '--verify', GH_PAGES_BRANCH]).exitCode) {
    console.log('Local ' + GH_PAGES_BRANCH +
      ' branch does not exist so try to fetch it')
    if (runGitCommand(['fetch', remote, GH_PAGES_BRANCH]).exitCode) {
      console.log(GH_PAGES_BRANCH + ' does not exist in remote, so creating...')
      runGitCommand(['checkout', '--orphan', GH_PAGES_BRANCH],
        'Unable to create new ' + GH_PAGES_BRANCH + ' branch')
      runGitCommand(['reset'], 'Unable to reset local ' + GH_PAGES_BRANCH +
        ' branch')
      runGitCommand(['commit', '--allow-empty', '-m', 'Initial commit'],
        'Unable to create initial ' + GH_PAGES_BRANCH + ' commit')
      runGitCommand(['clean', '-dfq'],
        'Unable to clean files before switching back to original branch')
      runGitCommand(['checkout', '--quiet', originalRef],
        'Unable to switch from ' + GH_PAGES_BRANCH +
        ' back to the original branch')
    } else {
      console.log('Creating local ' + GH_PAGES_BRANCH +
        ' branch tracking remote...')
      runGitCommand(['branch', GH_PAGES_BRANCH,
        'remotes/' + remote + '/' + GH_PAGES_BRANCH],
        'Unable to create local ' + GH_PAGES_BRANCH + ' branch')
    }
    ghPagesBranchUpToDate = true
  }

  console.log('Setting up worktree for ' + GH_PAGES_DIR + ' directory...')
  runGitCommand(['worktree', 'prune'], 'Unable to prune worktrees')
  var worktreeList = runGitCommand(['worktree', 'list']).output
  if (!worktreeList.match(process.cwd() + '/' +
      GH_PAGES_DIR + '.*\\[' + GH_PAGES_BRANCH + '\\]')) {
    console.log(GH_PAGES_BRANCH + ' worktree not setup, so creating...')
    rimraf.sync(GH_PAGES_DIR)
    runGitCommand(['worktree', 'add', GH_PAGES_DIR, GH_PAGES_BRANCH])
  }

  process.chdir(GH_PAGES_DIR)

  if (!ghPagesBranchUpToDate) {
    console.log('Pulling latest changes from remote into ' + GH_PAGES_BRANCH +
      ' branch')
    runGitCommand(['clean', '-dfq'],
      'Unable to clean files on ' + GH_PAGES_BRANCH + ' branch')
    runGitCommand(['pull', remote, GH_PAGES_BRANCH])
  }

  console.log('Running doc task...')
  runCommand('npm', ['run', 'doc'], 'Doc task failed')

  console.log('Adding changed files to git index...')
  runGitCommand(['add', 'jsdoc/*'], 'Unable to add jsdoc/* files to index')
  if (stagedChangesInRepo().exitCode) {
    console.log('Committing changes to ' + GH_PAGES_BRANCH + ' branch...')
    var shortCommitSha = originalCommitSha.substring(0, 7)
    runGitCommand(['commit', '-m', 'Updating docs for ' + shortCommitSha],
      'Unable to commit changes')
  } else {
    console.log(GH_PAGES_BRANCH +
      ' branch already up to date, skipping commit...')
  }

  console.log('Pushing ' + GH_PAGES_BRANCH + ' changes to ' + remote + '...')
  runGitCommand(['push', remote, GH_PAGES_BRANCH], 'Unable to push changes')

  console.log('Publish was successful, exiting...')
  shutdown()
}

main()
