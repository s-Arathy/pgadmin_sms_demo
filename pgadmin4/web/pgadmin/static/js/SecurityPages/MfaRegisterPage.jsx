/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2025, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////
import { Box } from '@mui/material';
import React, { useState, useMemo } from 'react';
import LoginImage from '../../img/login.svg?svgr';
import { FormNote, InputText } from '../components/FormComponents';
import BasePage, { SecurityButton } from './BasePage';
import { DefaultButton } from '../components/Buttons';
import gettext from 'sources/gettext';
import PropTypes from 'prop-types';
import _ from 'lodash';

function EmailRegisterView({mfaView}) {
  const [inputEmail, setInputEmail] = useState(mfaView.email_address || '');
  const [inputCode, setInputCode] = useState('');
  const [error, setError] = useState('');

  const handleEmailChange = (e) => {
    const email = e.target.value;
    setInputEmail(email);
    // Basic email validation
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError('Please enter a valid email address');
    } else {
      setError('');
    }
  };

  const handleCodeChange = (e) => {
    const code = e.target.value;
    setInputCode(code);
    if (!code.match(/^\d{6}$/)) {
      setError('Please enter a valid 6-digit code');
    } else {
      setError('');
    }
  };

  if(mfaView.email_address_placeholder) {
    return <>
      <div style={{textAlign: 'center', fontSize: '1.2em'}} data-test="email-register-view">{mfaView.label}</div>
      <div>
        <input type='hidden' name="auth_method" value={mfaView.auth_method}/>
        <input type='hidden' name={mfaView.auth_method} value='SETUP'/>
        <input type='hidden' name='validate' value='send_code'/>
      </div>
      <div>{mfaView.description}</div>
      <InputText 
        value={inputEmail} 
        type="email" 
        name="send_to" 
        placeholder={mfaView.email_address_placeholder}
        onChange={handleEmailChange} 
        required
        pattern="[^\s@]+@[^\s@]+\.[^\s@]+"
        data-test="email-input"
      />
      {error && <div style={{color: 'red', fontSize: '0.8em'}}>{error}</div>}
      <FormNote text={mfaView.note} />
    </>;
  } else if(mfaView.otp_placeholder) {
    return <>
      <div style={{textAlign: 'center', fontSize: '1.2em'}} data-test="email-register-view">{mfaView.label}</div>
      <div>
        <input type='hidden' name="auth_method" value={mfaView.auth_method}/>
        <input type='hidden' name={mfaView.auth_method} value='SETUP'/>
        <input type='hidden' name='validate' value='verify_code'/>
      </div>
      <div>{mfaView.message}</div>
      <InputText 
        value={inputCode} 
        pattern="\d{6}" 
        type="password" 
        name="code" 
        placeholder={mfaView.otp_placeholder}
        onChange={handleCodeChange} 
        required 
        autoComplete="one-time-code"
        maxLength="6"
        data-test="code-input"
      />
      {error && <div style={{color: 'red', fontSize: '0.8em'}}>{error}</div>}
    </>;
  }
  return null;
}

EmailRegisterView.propTypes = {
  mfaView: PropTypes.object,
};

function AuthenticatorRegisterView({mfaView}) {
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');

  const handleCodeChange = (e) => {
    const code = e.target.value;
    setInputValue(code);
    // Basic code validation
    if (!code.match(/^\d{6}$/)) {
      setError('Please enter a valid 6-digit code');
    } else {
      setError('');
    }
  };

  return <>
    <div style={{textAlign: 'center', fontSize: '1.2em'}} data-test="auth-register-view">{mfaView.auth_title}</div>
    <div>
      <input type='hidden' name="auth_method" value={mfaView.auth_method}/>
      <input type='hidden' name={mfaView.auth_method} value='SETUP'/>
      <input type='hidden' name='VALIDATE' value='validate'/>
    </div>
    <div style={{minHeight: 0, display: 'flex', justifyContent: 'center'}}>
      <img 
        src={`data:image/jpeg;base64,${mfaView.image}`} 
        style={{maxWidth: '200px', objectFit: 'contain'}} 
        alt={mfaView.qrcode_alt_text} 
      />
    </div>
    <div>{mfaView.auth_description}</div>
    <InputText 
      value={inputValue} 
      type="password" 
      name="code" 
      placeholder={mfaView.otp_placeholder}
      onChange={handleCodeChange}
      required
      pattern="\d{6}"
      maxLength="6"
      autoComplete="one-time-code"
    />
    {error && <div style={{color: 'red', fontSize: '0.8em'}}>{error}</div>}
  </>;
}

AuthenticatorRegisterView.propTypes = {
  mfaView: PropTypes.object,
};

function SMSRegisterView({mfaView}) {
  const [inputPhone, setInputPhone] = useState(mfaView?.phone_number || '');
  const [inputCode, setInputCode] = useState('');
  const [error, setError] = useState('');
  const uniqueId = useMemo(() => _.uniqueId('sms_'), []);

  const handlePhoneChange = (e) => {
    const phone = e.target.value;
    setInputPhone(phone);
    setError(''); // Clear error while typing
  };

  const handleCodeChange = (e) => {
    const code = e.target.value;
    setInputCode(code);
    setError(''); // Clear error while typing
  };

  // Phone number input view
  if(mfaView?.phone_number_placeholder) {
    return (
      <div className="sms-register-form" data-test="sms-register-view">
        <div style={{textAlign: 'center', fontSize: '1.2em'}}>{mfaView.label}</div>
        <div>
          <input type='hidden' name="auth_method" value={mfaView.auth_method}/>
          <input type='hidden' name={mfaView.auth_method} value='SETUP'/>
          <input type='hidden' name='validate' value='send_code'/>
        </div>
        <div>{mfaView.description}</div>
        <InputText 
          id={`${uniqueId}_phone`}
          value={inputPhone} 
          type="tel" 
          name="send_to" 
          placeholder={mfaView.phone_number_placeholder}
          pattern="^\+[1-9]\d{1,14}$"
          onChange={handlePhoneChange}
          required 
          data-test="phone-input"
          autoComplete="tel"
          title="Enter phone number with country code (e.g., +919567283578)"
        />
        {error && <div style={{color: 'red', fontSize: '0.8em'}}>{error}</div>}
        <FormNote text={mfaView.note} />
      </div>
    );
  }
  
  // Verification code input view
  if(mfaView?.otp_placeholder) {
    return (
      <div className="sms-verify-form" data-test="sms-register-view">
        <div style={{textAlign: 'center', fontSize: '1.2em'}}>{mfaView.label}</div>
        <div>
          <input type='hidden' name="auth_method" value={mfaView.auth_method}/>
          <input type='hidden' name={mfaView.auth_method} value='SETUP'/>
          <input type='hidden' name='validate' value='verify_code'/>
        </div>
        <div>{mfaView.message}</div>
        <InputText 
          id={`${uniqueId}_code`}
          value={inputCode} 
          pattern="\d{6}" 
          type="password" 
          name="code" 
          placeholder={mfaView.otp_placeholder}
          onChange={handleCodeChange}
          required 
          autoComplete="one-time-code"
          maxLength="6"
          data-test="code-input"
          inputMode="numeric"
        />
        {error && <div style={{color: 'red', fontSize: '0.8em'}}>{error}</div>}
      </div>
    );
  }
  
  return null;
}

SMSRegisterView.propTypes = {
  mfaView: PropTypes.object,
};

export default function MfaRegisterPage({actionUrl, mfaList, nextUrl, mfaView, ...props}) {
  const handleSubmit = (e) => {
    // Only prevent submission if there's an error
    if (e.target.querySelector('[style*="color: red"]')) {
      e.preventDefault();
      return false;
    }
    return true;
  };

  return (
    <BasePage title={gettext('Authentication Registration')} pageImage={<LoginImage style={{height: '100%', width: '100%'}} />} {...props}>
      <form 
        style={{
          display:'flex', 
          gap:'15px', 
          flexDirection:'column', 
          minHeight: 0,
          maxWidth: '400px',
          margin: '0 auto',
          padding: '1rem'
        }} 
        action={actionUrl} 
        method="POST"
        onSubmit={handleSubmit}
      >
        <input type="hidden" name="csrf_token" value={window.pgAdmin.csrf_token_header} />
        {mfaView ? <>
          {mfaView.auth_method === 'email' && <EmailRegisterView mfaView={mfaView} />}
          {mfaView.auth_method === 'authenticator' && <AuthenticatorRegisterView mfaView={mfaView} />}
          {mfaView.auth_method === 'sms' && <SMSRegisterView mfaView={mfaView} />}
          <Box display="flex" gap="15px">
            <SecurityButton type="submit" name="continue" value="Continue">
              {gettext('Continue')}
            </SecurityButton>
            <DefaultButton type="submit" name="cancel" value="Cancel" style={{width: '100%'}}>
              {gettext('Cancel')}
            </DefaultButton>
          </Box>
        </> : <>
          {mfaList?.map((m)=>{
            return (
              <Box display="flex" width="100%" key={m.label} alignItems="center" padding="0.5rem">
                <div style={{
                  width: '40px',
                  height: '40px',
                  mask: `url(${m.icon})`,
                  maskRepeat: 'no-repeat',
                  maskPosition: 'center',
                  WebkitMask: `url(${m.icon})`,
                  WebkitMaskRepeat: 'no-repeat',
                  WebkitMaskPosition: 'center',
                  backgroundColor: '#fff',
                  marginRight: '1rem'
                }}>
                </div>
                <div style={{flex: 1}}>{m.label}</div>
                <div>
                  <SecurityButton 
                    type="submit" 
                    name={m.id} 
                    value={m.registered ? 'DELETE' : 'SETUP'}
                    data-auth-method={m.id}
                  >
                    {m.registered ? gettext('Delete') : gettext('Setup')}
                  </SecurityButton>
                </div>
              </Box>
            );
          })}
          {nextUrl !== 'internal' && 
            <SecurityButton type="submit" value="Continue">
              {gettext('Continue')}
            </SecurityButton>
          }
        </>}
        <input type="hidden" name="next" value={nextUrl}/>
      </form>
    </BasePage>
  );
}

MfaRegisterPage.propTypes = {
  actionUrl: PropTypes.string,
  mfaList: PropTypes.arrayOf(PropTypes.object),
  nextUrl: PropTypes.string,
  mfaView: PropTypes.object
};
